from constraintManager import *
from ui.uiElement import *

from window import *

import pygame

from abc import ABC, abstractmethod

class Scene:
    def __init__(self, window, name):
        self.window = window
        self.name = name

        self.dim = self.window.screen.get_size()
        constraints = [
            ABSOLUTE(T_X, 0),
            ABSOLUTE(T_Y, Window.TAB_HEIGHT),
            RELATIVE(T_W, 1, P_W),
            COMPOUND(RELATIVE(T_H, 1, P_H), ABSOLUTE(T_H, -Window.TAB_HEIGHT))
        ]
        self.sceneWrapper = UiWrapper(self.window, constraints)
    @abstractmethod
    def createUi(self):
        ...
    @abstractmethod
    def handleUiEvents(self, event):
        ...
    @abstractmethod
    def absUpdate(self, delta):
        ...
    @abstractmethod
    def start(self):
        ...
    @abstractmethod
    def stop(self):
        ...
    
    def eventHandler(self, event):
        self.handleUiEvents(event)
        return
    
    def update(self, delta):
        self.absUpdate(delta)
        return
