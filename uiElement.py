from constraintManager import *
from asset import *

import numpy as np

from abc import ABC, abstractmethod
import time
import OpenGL.GL as GL

from py3d.core.base import Base
from py3d.core.utils import Utils
from py3d.core.attribute import Attribute
from py3d.core.uniform import Uniform

import pygame

from mjpeg.client import MJPEGClient

import glm

from PIL import Image
from io import BytesIO

class UiElement:
    def __init__(self, window, constraints, dim=(0,0,0,0)):
        self.window = window
        self.constraints = constraints
        self.children = []
        self.parent = None
        self.isDirty = True
        self.dim = dim
        self.constraintManager = ConstraintManager((self.dim[0], self.dim[1]), (self.dim[2], self.dim[3]))
        self.lastMouseState = self.window.mouseButtons

        self.vertices = [[0,0,0],[0,0,0],[0,0,0],[0,0,0]]

        self.type = 'nothing'

        self.defaultCall = None
        self.pressCall = None
        self.releaseCall = None
        self.hoverCall = None

    def update(self):
        if self.isDirty and self.parent != None:
            relDim = self.parent.constraintManager.calcConstraints(*self.constraints)
            self.dim = (relDim[0] + self.parent.dim[0], relDim[1] + self.parent.dim[1], relDim[2], relDim[3])
            self.vertices = [[0,0,0],[1,0,0],[1,1,0],[0,1,0]]
            self.constraintManager.parentPos = (self.dim[0], self.dim[1])
            self.constraintManager.parentDim = (self.dim[2], self.dim[3])
            self.isDirty = False
        for child in self.children:
            child.update()
        self.actions()
        self.absUpdate()
    @abstractmethod
    def absUpdate(self):
        ...
    
    def render(self):
        self.absRender()
        for child in self.children:
            child.render()
    @abstractmethod
    def absRender(self):
        ...
    
    def actions(self):
        mousePos = self.window.mousePos
        if mousePos[0] > self.dim[0] and mousePos[0] < self.dim[0] + self.dim[2] and mousePos[1] > self.dim[1] and mousePos[1] < self.dim[1] + self.dim[3]:
            if self.window.mouseButtons[0] and not self.lastMouseState[0]:
                self.onPress(self.pressCall)
            if not self.window.mouseButtons[0] and self.lastMouseState[0]:
                self.onRelease(self.releaseCall)
            if not self.window.mouseButtons[0] and not self.lastMouseState[0]:
                self.onHover(self.hoverCall)
        else:
            self.onDefault(self.defaultCall)
        self.lastMouseState = self.window.mouseButtons
    
    def onDefault(self, callback=None):
        return
    
    def onHover(self, callback=None):
        return
    
    def onPress(self, callback=None):
        self.window.uiEvents.append({'obj':self, 'action':'press', 'type':self.type, 'time':time.time_ns()})
    
    def onRelease(self, callback=None):
        self.window.uiEvents.append({'obj':self, 'action':'release', 'type':self.type, 'time':time.time_ns()})

    def addChild(self, child):
        if child.parent != None: return
        if child in self.children: return
        self.setDirty()
        self.children.append(child)
        child.parent = self
    
    def addChildren(self, *children):
        for child in children:
            self.addChild(child)
    
    def removeChild(self, child):
        if child.parent != self: return
        if not child in self.children: return
        child.setDirty()
        self.children.remove(child)
        child.parent = None
    
    def removeChildren(self, *children):
        for child in children:
            self.removeChild(child)
    
    def setDirty(self):
        self.isDirty = True
        for child in self.children:
            child.setDirty()

class GlElement:
    def __init__(self, window, constraints, shader, dim=(0,0,0,0)):
        self.window = window
        self.constraints = constraints
        self.shader = shader
        self.dim = dim

        self.children = []
        self.parent = None
        self.isDirty = True
        self.constraintManager = ConstraintManager((self.dim[0], self.dim[1]), (self.dim[2], self.dim[3]))
        self.lastMouseState = self.window.mouseButtons

        self.vertices = np.array([[-0.5, -0.5, 0.0],
                                  [-0.5,  0.5, 0.0],
                                  [ 0.5,  0.5, 0.0],
                                  [ 0.5, -0.5, 0.0]], dtype = 'float32')
        self.indices = np.array([1,2,0,2,3,0], dtype='int32')

        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)
        self.vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        self.ebo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.indices, GL.GL_DYNAMIC_DRAW)

        self.verticesAttrib = Attribute('vec3', self.vertices)
        self.verticesAttrib.associate_variable(self.shader, 'position')
        self.translation = Uniform('vec3', [0.0, 0.0, 0.0])
        self.translation.locate_variable(self.shader, 'translation')
        self.baseColor = Uniform('vec3', [1.0, 0.8, 0.8])
        self.baseColor.locate_variable(self.shader, 'baseColor')

        self.type = 'nothing'

        self.defaultCall = None
        self.pressCall = None
        self.releaseCall = None
        self.hoverCall = None

    def update(self):
        if self.isDirty and self.parent != None:
            relDim = self.parent.constraintManager.calcConstraints(*self.constraints)
            self.dim = (relDim[0] + self.parent.dim[0], relDim[1] + self.parent.dim[1], relDim[2], relDim[3])
            openglDim = (
                (2*self.dim[0])/self.window.dim[0] - 1,
                (2*(self.window.dim[1]-self.dim[1]-self.dim[3]))/self.window.dim[1] - 1,
                (2*self.dim[2])/self.window.dim[0],
                (2*self.dim[3])/self.window.dim[1],
            )
            self.vertices = np.array([[openglDim[0],openglDim[1],0.0],
                                      [openglDim[0],openglDim[1]+openglDim[3],0.0],
                                      [openglDim[0]+openglDim[2],openglDim[1]+openglDim[3], 0.0],
                                      [openglDim[0]+openglDim[2],openglDim[1],0.0]], dtype = 'float32')
            
            self.constraintManager.parentPos = (self.dim[0], self.dim[1])
            self.constraintManager.parentDim = (self.dim[2], self.dim[3])

            self.verticesAttrib.data = self.vertices
            self.verticesAttrib.upload_data()

            self.isDirty = False
        for child in self.children:
            child.update()
        self.actions()
        self.absUpdate()
        return
    @abstractmethod
    def absUpdate(self):
        ...
    
    def render(self):
        self.absRender()
        for child in self.children:
            child.render()
    @abstractmethod
    def absRender(self):
        ...
    
    def actions(self):
        mousePos = self.window.mousePos
        if mousePos[0] > self.dim[0] and mousePos[0] < self.dim[0] + self.dim[2] and mousePos[1] > self.dim[1] and mousePos[1] < self.dim[1] + self.dim[3]:
            if self.window.mouseButtons[0] and not self.lastMouseState[0]:
                self.onPress(self.pressCall)
            if not self.window.mouseButtons[0] and self.lastMouseState[0]:
                self.onRelease(self.releaseCall)
            if not self.window.mouseButtons[0] and not self.lastMouseState[0]:
                self.onHover(self.hoverCall)
        else:
            self.onDefault(self.defaultCall)
        self.lastMouseState = self.window.mouseButtons

    def onDefault(self, callback=None):
        return
    
    def onHover(self, callback=None):
        return
    
    def onPress(self, callback=None):
        self.window.uiEvents.append({'obj':self, 'action':'press', 'type':self.type, 'time':time.time_ns()})
    
    def onRelease(self, callback=None):
        self.window.uiEvents.append({'obj':self, 'action':'release', 'type':self.type, 'time':time.time_ns()})

    def addChild(self, child):
        if child.parent != None: return
        if child in self.children: return
        self.setDirty()
        self.children.append(child)
        child.parent = self
    
    def addChildren(self, *children):
        for child in children:
            self.addChild(child)
    
    def removeChild(self, child):
        if child.parent != self: return
        if not child in self.children: return
        child.setDirty()
        self.children.remove(child)
        child.parent = None
    
    def removeChildren(self, *children):
        for child in children:
            self.removeChild(child)
    
    def setDirty(self):
        self.isDirty = True
        for child in self.children:
            child.setDirty()

    def setColor(self, color):
        self.baseColor.data = [*color]

    def setTranslate(self, translate=(0,0,0)):
        self.translate.data = [*translate]

class UiButton(GlElement):
    def __init__(self, window, constraints, shader, dim=(0,0,0,0)):
        super().__init__(window, constraints, shader, dim)
        self.type = 'button'
        self.font = Assets.VERA_FONT
        

        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)

        self.textIndices = np.array([1,0,3,3,1,2], dtype='int32')
        
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        
        self.textVao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.textVao)

        self.textVbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.textVbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, 4 * 4 * 4, None, GL.GL_DYNAMIC_DRAW)

        GL.glVertexAttribPointer(0, 4, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
        GL.glEnableVertexAttribArray(0)
        
        self.textEbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.textEbo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.textIndices, GL.GL_DYNAMIC_DRAW)

        # unbind vao vbo ebo
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        # GL.glUseProgram(Assets.TEXT_SHADER)
        # shader_projection = GL.glGetUniformLocation(Assets.TEXT_SHADER, "projection")
        # projection = glm.ortho(0, 1600, 1000, 0)
        # GL.glUniformMatrix4fv(shader_projection, 1, GL.GL_FALSE, glm.value_ptr(projection))

        # GL.glEnableVertexAttribArray(0)
        # GL.glVertexAttribPointer(0, 4, GL.GL_FLOAT, GL.GL_FALSE, 0, None)

        # GL.glBindVertexArray(self.textVao)
        # GL.glBindVertexArray(0)

    def absUpdate(self):
        return
        # self.textRect.center = (self.dim[0] + self.dim[2] // 2, self.dim[1] + self.dim[3] // 2)

    def absRender(self):
        GL.glUseProgram(self.shader)

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)

        self.translation.upload_data()
        self.baseColor.upload_data()

        GL.glDrawElements(GL.GL_TRIANGLES, len(self.indices), GL.GL_UNSIGNED_INT, None)

        self.renderText('abcdefghijklmnopqrstuvwxyz', Assets.FIRACODE_FONT, 2)
        return
    
    def renderText(self, text, font, scale):
        GL.glUseProgram(Assets.TEXT_SHADER)

        GL.glBindVertexArray(self.textVao)

        GL.glUniform3f(GL.glGetUniformLocation(Assets.TEXT_SHADER, "textColor"), 1, 1, 1)

        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        x = self.dim[0]
        y = self.dim[1]
        for c in text:
            ch = font[c]
            w, h = ch.textureSize
            yoff = 0

            # print(f'{c}: {h} | {ch.descender} | {ch.ascender}')

            vertices = self.getVertexData(x,y - ch.descender*scale,w*scale,(ch.ascender + ch.descender)*scale)

            #render glyph texture over quad
            GL.glBindTexture(GL.GL_TEXTURE_2D, ch.texture)
            #update content of VBO memory
            
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.textVbo)
            GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

            #render quad
            GL.glBindVertexArray(self.textVao)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.textVbo)
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.textEbo)
            GL.glEnableVertexAttribArray(0)
            GL.glDrawElements(GL.GL_TRIANGLES, len(self.textIndices), GL.GL_UNSIGNED_INT, None)
            GL.glDisableVertexAttribArray(0)
            #now advance cursors for next glyph (note that advance is number of 1/64 pixels)
            x += w*scale + 5*scale

        GL.glBindVertexArray(0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    # def setText(self, text):
    #     self.text = self.font.render(text, 1, (255,255,255))
    #     self.textRect = self.text.get_rect()
    #     self.textRect.center = (self.dim[0] + self.dim[2] // 2, self.dim[1] + self.dim[3] // 2)

    def getVertexData(self, xpos, ypos, w, h):
        xpos = (2*xpos)/self.window.dim[0] - 1
        ypos = (2*ypos)/self.window.dim[1] - 1
        w = (2*w)/self.window.dim[0]
        h = (2*h)/self.window.dim[1]
        return np.array([
            xpos,       ypos + h, 0, 0,
            xpos,       ypos,     0, 1,
            xpos + w,   ypos,     1, 1,
            xpos + w,   ypos + h, 1, 0
        ], np.float32)

class UiText(GlElement):
    def __init__(self, window, constraints, dim=(0,0,0,0)):
        super().__init__(window, constraints, Assets.TEST_SHADER, dim)
        self.type = 'button'
        
        self.dirtyText = True
        self.font = Assets.FIRACODE_FONT
        self.text = 'abcdefghijklmnopqrstuvwxyz'
        self.fontSize = 48
        self.textSpacing = 5

        self.maxDescender = 0
        self.maxAscender = 0

        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)

        self.textIndices = np.array([1,0,3,3,1,2], dtype='int32')
        
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        
        self.textVao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.textVao)

        self.textVbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.textVbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, 4 * 4 * 4, None, GL.GL_DYNAMIC_DRAW)

        GL.glVertexAttribPointer(0, 4, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
        GL.glEnableVertexAttribArray(0)
        
        self.textEbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.textEbo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.textIndices, GL.GL_DYNAMIC_DRAW)

        # unbind vao vbo ebo
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def absUpdate(self):
        self.updateTextBound()
        return
    
    def updateTextBound(self):
        if not self.dirtyText:
            return
        maxdes = 0
        maxasc = 0
        x = self.dim[0]
        xStart = x
        y = self.dim[1]
        for c in self.text:
            ch = self.font[c]
            w, h = ch.textureSize
            maxdes = max(maxdes, ch.descender)
            maxasc = max(maxasc, ch.ascender)

            x += w + self.textSpacing
        widthAspect = (x-xStart)/(maxasc+maxdes)
        
        self.maxAscender = maxasc
        self.maxDescender = maxdes

        # find width constraint
        widthConstraint = None
        heightConstraint = None
        for c in self.constraints:
            if c.toChange == T_W:
                widthConstraint = c
            if c.toChange == T_H:
                heightConstraint = c
        
        self.constraints.remove(widthConstraint)
        self.constraints.remove(heightConstraint)
        self.constraints.append(RELATIVE(T_W, widthAspect, T_H))
        self.constraints.append(ABSOLUTE(T_H, self.fontSize))
        self.setDirty()
        self.dirtyText = False

    def absRender(self):
        GL.glUseProgram(self.shader)

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)

        self.translation.upload_data()
        self.baseColor.upload_data()

        GL.glDrawElements(GL.GL_TRIANGLES, len(self.indices), GL.GL_UNSIGNED_INT, None)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        self.renderText(self.text, Assets.FIRACODE_FONT, self.fontSize/48)
        return
    
    def renderText(self, text, font, scale):
        GL.glUseProgram(Assets.TEXT_SHADER)

        GL.glBindVertexArray(self.textVao)

        GL.glUniform3f(GL.glGetUniformLocation(Assets.TEXT_SHADER, "textColor"), 1, 1, 1)

        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        x = self.dim[0]
        y = self.dim[1]
        for c in text:
            ch = font[c]
            w, h = ch.textureSize
            w = w*scale
            h = h*scale
            des = ch.descender*scale

            vertices = self.getVertexData(x, y + des + self.maxAscender, w, h)

            #render glyph texture over quad
            GL.glBindTexture(GL.GL_TEXTURE_2D, ch.texture)
            #update content of VBO memory
            
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.textVbo)
            GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

            #render quad
            GL.glBindVertexArray(self.textVao)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.textVbo)
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.textEbo)
            GL.glEnableVertexAttribArray(0)
            GL.glDrawElements(GL.GL_TRIANGLES, len(self.textIndices), GL.GL_UNSIGNED_INT, None)
            GL.glDisableVertexAttribArray(0)
            #now advance cursors for next glyph (note that advance is number of 1/64 pixels)
            x += w*scale + self.textSpacing*scale

        GL.glBindVertexArray(0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def getVertexData(self, xpos, ypos, w, h):
        xpos = (2*xpos)/self.window.dim[0] - 1
        ypos = (2*(self.window.dim[1]-ypos))/self.window.dim[1] - 1
        w = (2*w)/self.window.dim[0]
        h = (2*h)/self.window.dim[1]
        return np.array([
            xpos,       ypos + h, 0, 0,
            xpos,       ypos,     0, 1,
            xpos + w,   ypos,     1, 1,
            xpos + w,   ypos + h, 1, 0
        ], np.float32)

class UiWrapper(GlElement):
    def __init__(self, window, constraints, shader, dim=(0,0,0,0)):
        super().__init__(window, constraints, shader, dim)
        self.type = 'wrapper'

    def absUpdate(self):
        return

    def absRender(self):
        return
    
    def onPress(self, callback=None):
        return
    
    def onRelease(self, callback=None):
        return

class UiStream(GlElement):
    def __init__(self, window, constraints, shader, url, dim=(0,0,0,0)):
        super().__init__(window, constraints, shader, dim)
        self.type = 'stream'

        self.url = url
        try:
            self.client = MJPEGClient(self.url)
            bufs = self.client.request_buffers(65536, 50)
            for b in bufs:
                self.client.enqueue_buffer(b)
            self.client.start()
        except:
            pass
        self.image = None

    def pilConv(self, pilImage):
        return pygame.image.fromstring(
            pilImage.tobytes(), pilImage.size, pilImage.mode).convert()

    def absUpdate(self):
        buf = self.client.dequeue_buffer()
        stream = BytesIO(buf.data)
        self.client.enqueue_buffer(buf)
        image = Image.open(stream).convert("RGB")
        stream.close()
        image = image.resize((int(self.dim[2]), int(self.dim[3])))
        self.image = self.pilConv(image)
        return

    def absRender(self):
        if self.image != None:
            self.window.screen.blit(self.image, (self.dim[0], self.dim[1]))
    
    def onPress(self, callback=None):
        return
    
    def onRelease(self, callback=None):
        return





