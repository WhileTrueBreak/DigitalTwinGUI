from constraintManager import *
from uiElement import *
from opcua import Opcua

import pygame

from abc import ABC, abstractmethod

class Scene:
    def __init__(self, window, name, opcua=None):
        self.name = name

        self.opcua = opcua

        self.window = window
        self.dim = self.window.dim
        constraints = [
            ABSOLUTE(T_X, 0),
            ABSOLUTE(T_Y, self.window.tabHeight),
            RELATIVE(T_W, 1, P_W),
            COMPOUND(RELATIVE(T_H, 1, P_H), ABSOLUTE(T_H, -self.window.tabHeight))
        ]
        self.sceneWrapper = UiWrapper(self.window, constraints)

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
