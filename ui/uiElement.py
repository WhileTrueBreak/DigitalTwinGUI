from constraintManager import *
from asset import *
from mathHelper import *
from modelRenderer import *
from mjpegThread import *

import numpy as np

from abc import abstractmethod
import time
import OpenGL.GL as GL

from mjpeg.client import MJPEGClient

from PIL import Image
from PIL.Image import Transpose

import ctypes

class GlElement:
    def __init__(self, window, constraints, dim=(0,0,0,0)):
        self.window = window
        self.constraints = constraints
        self.dim = dim
        self.openGLDim = self.dim

        self.children = []
        self.parent = None
        self.isDirty = True
        self.constraintManager = ConstraintManager((self.dim[0], self.dim[1]), (self.dim[2], self.dim[3]))
        self.lastMouseState = self.window.mouseButtons

        self.type = 'nothing'

    def update(self, delta):
        if self.isDirty and self.parent != None:
            relDim = self.parent.constraintManager.calcConstraints(*self.constraints)
            self.dim = (relDim[0] + self.parent.dim[0], relDim[1] + self.parent.dim[1], relDim[2], relDim[3])
            self.openGLDim = (
                (2*self.dim[0])/self.window.dim[0] - 1,
                (2*(self.window.dim[1]-self.dim[1]-self.dim[3]))/self.window.dim[1] - 1,
                (2*self.dim[2])/self.window.dim[0],
                (2*self.dim[3])/self.window.dim[1],
            )
            self.constraintManager.pos = (self.dim[0], self.dim[1])
            self.constraintManager.dim = (self.dim[2], self.dim[3])
            self.reshape()
            self.isDirty = False
        for child in self.children:
            child.update(delta)
        self.actions()
        self.absUpdate(delta)
        return
    @abstractmethod
    def reshape(self):
        ...
    @abstractmethod
    def absUpdate(self, delta):
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
        self.isDefault = False
        if mousePos[0] > self.dim[0] and mousePos[0] < self.dim[0] + self.dim[2] and mousePos[1] > self.dim[1] and mousePos[1] < self.dim[1] + self.dim[3]:
            self.isDefault = False
            if self.window.mouseButtons[0] and not self.lastMouseState[0]:
                self.onPress()
            elif not self.window.mouseButtons[0] and self.lastMouseState[0]:
                self.onRelease()
            elif not self.window.mouseButtons[0] and not self.lastMouseState[0]:
                self.onHover()
            else:
                self.onHeld()
        elif not self.isDefault:
            self.onDefault()
            self.isDefault = True
        self.lastMouseState = self.window.mouseButtons

    def onDefault(self, callback=None):
        return
    
    def onHover(self, callback=None):
        return
    
    def onPress(self, callback=None):
        return
    
    def onRelease(self, callback=None):
        return
    
    def onHeld(self, callback=None):
        return

    def addChild(self, child):
        if child.parent != None: return
        if child in self.children: return
        child.setDirty()
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

class UiButton(GlElement):
    def __init__(self, window, constraints, dim=(0,0,0,0)):
        super().__init__(window, constraints, dim)
        self.type = 'button'

        self.shader = Assets.SOLID_SHADER
        self.currentColor = (1, 1, 1)
        self.defaultColor = (1, 1, 1)
        self.hoverColor = (1, 1, 1)
        self.pressColor = (1, 1, 1)

        self.vertices = np.array([
            [self.openGLDim[0], self.openGLDim[1], *self.currentColor],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1], *self.currentColor],
            [self.openGLDim[0], self.openGLDim[1]+self.openGLDim[3], *self.currentColor],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1]+self.openGLDim[3], *self.currentColor]
        ], dtype='float32')
        self.indices = np.array([1, 0, 3, 3, 0, 2], dtype='int32')

        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)

        self.vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertices, GL.GL_DYNAMIC_DRAW)

        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 5*4, ctypes.c_void_p(0*4))
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_TRUE, 5*4, ctypes.c_void_p(2*4))
        GL.glEnableVertexAttribArray(1)

        self.ebo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.indices, GL.GL_DYNAMIC_DRAW)

        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def reshape(self):
        self.vertices = np.array([
            [self.openGLDim[0], self.openGLDim[1], *self.currentColor],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1], *self.currentColor],
            [self.openGLDim[0], self.openGLDim[1]+self.openGLDim[3], *self.currentColor],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1]+self.openGLDim[3], *self.currentColor]
        ], dtype='float32')
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, self.vertices.nbytes, self.vertices)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        return

    def absUpdate(self, delta):
        return

    def absRender(self):
        GL.glUseProgram(self.shader)
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)

        GL.glEnableVertexAttribArray(0)
        GL.glEnableVertexAttribArray(1)

        GL.glDrawElements(GL.GL_TRIANGLES, len(self.indices), GL.GL_UNSIGNED_INT, None)

        GL.glDisableVertexAttribArray(1)
        GL.glDisableVertexAttribArray(0)
        return

    def setColor(self, color):
        self.currentColor = color
        self.reshape()
        return

    def setDefaultColor(self, color):
        self.defaultColor = color

    def setHoverColor(self, color):
        self.hoverColor = color

    def setPressColor(self, color):
        self.pressColor = color

    def onDefault(self, callback=None):
        self.setColor(self.defaultColor)
    
    def onHover(self, callback=None):
        self.setColor(self.hoverColor)
    
    def onHeld(self, callback=None):
        self.setColor(self.pressColor)

    def onPress(self, callback=None):
        self.window.uiEvents.append({'obj':self, 'action':'press', 'type':self.type, 'time':time.time_ns()})
    
    def onRelease(self, callback=None):
        self.window.uiEvents.append({'obj':self, 'action':'release', 'type':self.type, 'time':time.time_ns()})

class UiText(GlElement):
    def __init__(self, window, constraints, dim=(0,0,0,0)):
        constraints.append(ABSOLUTE(T_W, 0))
        constraints.append(ABSOLUTE(T_H, 0))
        super().__init__(window, constraints, dim)
        self.type = 'text'
        
        self.dirtyText = True
        self.font = Assets.FIRACODE_FONT
        self.text = 'default'
        self.fontSize = 48
        self.textSpacing = 5
        self.textColor = (1,1,1)

        self.maxDescender = 0
        self.maxAscender = 0

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
    
    def reshape(self):
        return

    def absUpdate(self, delta):
        self.updateTextBound()
        return
    
    def updateTextBound(self):
        if not self.dirtyText:
            return
        scale = self.fontSize/48
        
        maxdes = 0
        maxasc = 0
        x = self.dim[0]
        xStart = x
        y = self.dim[1]
        for c in self.text:
            ch = self.font[c]
            w, h = ch.textureSize
            maxdes = max(maxdes, ch.descender*scale)
            maxasc = max(maxasc, ch.ascender*scale)

            x += w*scale + self.textSpacing*scale
        x -= self.textSpacing*scale
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
        self.constraints.append(ABSOLUTE(T_H, self.maxDescender + self.maxAscender))
        self.setDirty()
        self.dirtyText = False

    def absRender(self):
        self.renderText(self.text, Assets.FIRACODE_FONT, self.fontSize/48)
        return
    
    def renderText(self, text, font, scale):
        GL.glUseProgram(Assets.TEXT_SHADER)

        GL.glBindVertexArray(self.textVao)

        GL.glUniform3f(GL.glGetUniformLocation(Assets.TEXT_SHADER, "textColor"), *self.textColor)

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
    
    def setText(self, text):
        self.text = text
        self.dirtyText = True
    
    def setFont(self, font):
        self.font = font
        self.dirtyText = True
    
    def setFontSize(self, size):
        self.fontSize = size
        self.dirtyText = True
    
    def setTextSpacing(self, spacing):
        self.textSpacing = spacing
        self.dirtyText = True

    def setTextColor(self, color):
        self.textColor = color

class UiWrapper(GlElement):
    def __init__(self, window, constraints, dim=(0,0,0,0)):
        super().__init__(window, constraints, dim)
        self.type = 'wrapper'

    def reshape(self):
        return

    def absUpdate(self, delta):
        return

    def absRender(self):
        return

class UiStream(GlElement):
    def __init__(self, window, constraints, url, dim=(0,0,0,0)):
        super().__init__(window, constraints, dim)
        self.type = 'stream'

        self.url = url
        self.container = StreamContainer()
        self.threadStopFlag = True
        self.thread = createMjpegThread(self.container, self.url, lambda:self.threadStopFlag)
        self.image = None

        self.vertices = np.array([
            [self.openGLDim[0], self.openGLDim[1], 0, 0],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1], 1, 0],
            [self.openGLDim[0], self.openGLDim[1]+self.openGLDim[3], 0, 1],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1]+self.openGLDim[3], 1, 1]
        ], dtype='float32')
        
        self.indices = np.array([1, 0, 3, 3, 0, 2], dtype='int32')

        self.texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)

        self.vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, 4 * 4 * 4, None, GL.GL_DYNAMIC_DRAW)

        GL.glVertexAttribPointer(0, 4, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
        GL.glEnableVertexAttribArray(0)
        
        self.ebo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.indices, GL.GL_DYNAMIC_DRAW)

        # unbind vao vbo ebo
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def reshape(self):
        self.vertices = np.array([
            [self.openGLDim[0], self.openGLDim[1], 0, 0],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1], 1, 0],
            [self.openGLDim[0], self.openGLDim[1]+self.openGLDim[3], 0, 1],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1]+self.openGLDim[3], 1, 1]
        ], dtype='float32')

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, self.vertices.nbytes, self.vertices)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        return

    def absUpdate(self, delta):
        self.updateImage(delta)
        return
    
    def updateImage(self, delta):
        stream = self.container.getStream()
        if stream == None: 
            return
        image = Image.open(stream).convert("RGBA")
        stream.close()
        self.image = image.transpose(Transpose.FLIP_TOP_BOTTOM).tobytes()

        self.texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)

        #texture options
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

        GL.glTexImage2D(
                GL.GL_TEXTURE_2D,    # where to load texture data
                0,                # mipmap level
                GL.GL_RGBA8,         # format to store data in
                image.width,                # image dimensions
                image.height,                #
                0,                # border thickness
                GL.GL_RGBA,          # format data is provided in
                GL.GL_UNSIGNED_BYTE, # type to read data as
                self.image)       # data to load as texture
        GL.glGenerateMipmap(GL.GL_TEXTURE_2D)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def absRender(self):
        GL.glUseProgram(Assets.STREAM_SHADER)

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)

        #render quad
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)

        GL.glEnableVertexAttribArray(0)
        GL.glDrawElements(GL.GL_TRIANGLES, len(self.indices), GL.GL_UNSIGNED_INT, None)
        GL.glDisableVertexAttribArray(0)
        
        return
    
    def start(self):
        self.threadStopFlag = False
        if self.thread.is_alive(): return
        self.thread = createMjpegThread(self.container, self.url, lambda:self.threadStopFlag)

    def stop(self):
        self.threadStopFlag = True

class Ui3DScene(GlElement):
    def __init__(self, window, constraints, supportTransparency=False, dim=(0,0,0,0)):
        super().__init__(window, constraints, dim)

        self.NEAR_PLANE = 0.1
        self.FAR_PLANE = 1000
        self.FOV = 80

        self.shader = Assets.SOLID_SHADER
        self.color = (1, 1, 1)
        self.vertices = np.array([
            [self.openGLDim[0], self.openGLDim[1], *self.color],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1], *self.color],
            [self.openGLDim[0], self.openGLDim[1]+self.openGLDim[3], *self.color],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1]+self.openGLDim[3], *self.color]
        ], dtype='float32')
        self.indices = np.array([1, 0, 3, 3, 0, 2], dtype='int32')

        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)

        self.vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertices, GL.GL_DYNAMIC_DRAW)

        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 5*4, ctypes.c_void_p(0*4))
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_TRUE, 5*4, ctypes.c_void_p(2*4))
        GL.glEnableVertexAttribArray(1)

        self.ebo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.indices, GL.GL_DYNAMIC_DRAW)

        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        self.modelRenderer = Renderer(self.window, supportTransparency)
        self.modelRenderer.setProjectionMatrix(createProjectionMatrix(self.dim[2], self.dim[3], self.FOV, self.NEAR_PLANE, self.FAR_PLANE))
        self.modelRenderer.setViewMatrix(createViewMatrix(0, 0, 0, 0, 0, 0))
        self.type = '3d scene'

    def reshape(self):
        self.modelRenderer.setProjectionMatrix(createProjectionMatrix(self.dim[2], self.dim[3], self.FOV, self.NEAR_PLANE, self.FAR_PLANE))
        self.vertices = np.array([
            [self.openGLDim[0], self.openGLDim[1], *self.color],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1], *self.color],
            [self.openGLDim[0], self.openGLDim[1]+self.openGLDim[3], *self.color],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1]+self.openGLDim[3], *self.color]
        ], dtype='float32')
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, self.vertices.nbytes, self.vertices)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        return

    def absUpdate(self, delta):
        return

    def absRender(self):
        GL.glUseProgram(self.shader)
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)

        GL.glEnableVertexAttribArray(0)
        GL.glEnableVertexAttribArray(1)

        GL.glDrawElements(GL.GL_TRIANGLES, len(self.indices), GL.GL_UNSIGNED_INT, None)

        GL.glDisableVertexAttribArray(1)
        GL.glDisableVertexAttribArray(0)

        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_DEPTH_TEST)

        GL.glViewport(int(self.dim[0]), int(self.window.dim[1]-self.dim[3]-self.dim[1]), int(self.dim[2]), int(self.dim[3]))
        
        self.modelRenderer.render()

        GL.glViewport(0, 0, *self.window.dim)

        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glDisable(GL.GL_CULL_FACE)
        return

    def setViewMatrix(self, matrix):
        self.modelRenderer.setViewMatrix(matrix)
    
    def getRenderer(self):
        return self.modelRenderer

    def setBackgroundColor(self, color):
        self.color = color
        self.reshape()
        return








