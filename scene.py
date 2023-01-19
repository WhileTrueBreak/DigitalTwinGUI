import pygame
import pygame_gui

from pygame_gui.ui_manager import UIManager
from pygame_gui.core import IncrementalThreadedResourceLoader, ObjectID

from pygame_gui.elements import *

from abc import ABC, abstractmethod

class Scene:
    def __init__(self, window, name):
        self.name = name

        self.window = window
        self.dim = self.window.dim
        self.loader = IncrementalThreadedResourceLoader()
        self.uiManager = UIManager(window.dim, '', resource_loader=self.loader)
    
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
        self.updateVariables(delta)
        self.uiManager.update(delta)
        return
    
    def render(self):
        self.uiManager.draw_ui(self.window.screen)
        return
