from utils.debug import *

import numpy as np

class StaticModel:
    
    @timing
    def __init__(self, window, renderer, model, transform):
        self.window = window
        self.renderer = renderer
        self.transform = transform
        self.modelId = self.renderer.addModel(model, transform)

        self.attach = None

    def update(self, delta):
        return
    
    def __updateTranforms(self):
        attachFrame = self.attach.getFrame() if self.attach else np.identity(4)
        self.renderer.setTransformMatrix(self.modelId, np.matmul(attachFrame, self.transform))
        return

    def handleEvents(self, event):
        return

    def start(self):
        return

    def stop(self):
        return

    def getControlPanel(self):
        return None

    def isModel(self, modelId):
        return modelId == self.modelId
    
    def setAttach(self, iModel):
        self.attach = iModel
        self.__updateTranforms()
        return
    
    def setTransform(self, transform):
        self.transform = transform
        self.__updateTranforms()