from ui.constraintManager import *

from ui.elements.uiWrapper import *

from window import *

from abc import abstractmethod

class Scene:
    def __init__(self, window, name):
        self.window = window
        self.name = name

        self.dim = self.window.screen.get_size()
        self.sceneWrapper = UiWrapper(self.window, Constraints.ALIGN_PERCENTAGE(0, 0, 1, 1))
    @abstractmethod
    def createUi(self):
        ...
    @abstractmethod
    def handleUiEvents(self, event):
        ...
    @abstractmethod
    def update(self, delta):
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
    
    def recUpdate(self, delta):
        self.update(delta)
        return
