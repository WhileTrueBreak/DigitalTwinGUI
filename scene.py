from constraintManager import *
from opcua import Opcua

import pygame
import pygame_gui

from pygame_gui.ui_manager import UIManager
from pygame_gui.core import IncrementalThreadedResourceLoader, ObjectID

from pygame_gui.elements import *

from abc import ABC, abstractmethod

class Scene:
    def __init__(self, window, name, opcua=None):
        self.name = name

        self.opcua = opcua
        if opcua == None: self.opcua = Opcua()

        self.window = window
        self.dim = self.window.dim
        self.uiManager = self.window.uiManager
        self.cManager = ConstraintManager((0, 0), self.dim)

        dim = self.cManager.calcConstraints(
            RELATIVE(T_W, 1, P_W),
            COMPOUND(RELATIVE(T_H, 1, P_H), ABSOLUTE(T_H, -30)),
            ABSOLUTE(T_X, 0),
            ABSOLUTE(T_Y, 30)
        )

        self.cManager.parentPos = (dim[0], dim[1])
        self.cManager.parentDim = (dim[2], dim[3])
        self.sceneContainer = pygame_gui.core.UIContainer(pygame.Rect(*dim),manager=self.uiManager)
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
        self.uiManager.update(delta)
        self.updateVariables(delta)
        return
    
    def render(self):
        self.uiManager.draw_ui(self.window.screen)
        return
