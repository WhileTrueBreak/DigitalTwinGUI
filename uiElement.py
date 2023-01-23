from constraintManager import *

from abc import ABC, abstractmethod
import time

import pygame

from mjpeg.client import MJPEGClient

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

        self.type = 'nothing'

        self.defaultCall = None
        self.pressCall = None
        self.releaseCall = None
        self.hoverCall = None

    def update(self):
        if self.isDirty and self.parent != None:
            relDim = self.parent.constraintManager.calcConstraints(*self.constraints)
            self.dim = (relDim[0] + self.parent.dim[0], relDim[1] + self.parent.dim[1], relDim[2], relDim[3])
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
    
    def setDirty(self):
        self.isDirty = True
        for child in self.children:
            child.setDirty()

class UiButton(UiElement):
    def __init__(self, window, constraints, dim=(0,0,0,0)):
        super().__init__(window, constraints, dim)
        self.type = 'button'
        self.font = pygame.font.SysFont("monospace", 18)
        self.setText('hello world')

    def absUpdate(self):
        self.textRect.center = (self.dim[0] + self.dim[2] // 2, self.dim[1] + self.dim[3] // 2)

    def absRender(self):
        pygame.draw.rect(self.window.screen, (0,0,0), self.dim)
        self.window.screen.blit(self.text, self.textRect)

    def setText(self, text):
        self.text = self.font.render(text, 1, (255,255,255))
        self.textRect = self.text.get_rect()
        self.textRect.center = (self.dim[0] + self.dim[2] // 2, self.dim[1] + self.dim[3] // 2)

class UiWrapper(UiElement):
    def __init__(self, window, constraints, dim=(0,0,0,0)):
        super().__init__(window, constraints, dim)
        self.type = 'wrapper'

    def absUpdate(self):
        return

    def absRender(self):
        return
    
    def onPress(self, callback=None):
        return
    
    def onRelease(self, callback=None):
        return

class UiStream(UiElement):
    def __init__(self, window, constraints, url, dim=(0,0,0,0)):
        super().__init__(window, constraints, dim)
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





