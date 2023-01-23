from constraintManager import *
from uiElement import *
from opcua import Opcua

import pygame

from abc import ABC, abstractmethod

class Scene:
    def __init__(self, window, name, opcua=None):
        self.name = name

        self.opcua = opcua
        if opcua == None: self.opcua = Opcua()

        self.window = window
        self.dim = self.window.dim
        dim = (0, self.window.tabHeight, self.window.dim[0], self.window.dim[1] - self.window.tabHeight)
        self.sceneWrapper = UiWrapper(self.window, [], dim)

    @abstractmethod
    def createUi(self):
        ...
    @abstractmethod
    def handleUiEvents(self, event):
        ...
    @abstractmethod
    def updateVariables(self, delta):
        ...

    def eventHandler(self, event):
        self.handleUiEvents(event)
        return
    
    def update(self, delta):
        self.sceneWrapper.update()
        self.updateVariables(delta)
        return
    
    def render(self):
        self.sceneWrapper.render()
        return
