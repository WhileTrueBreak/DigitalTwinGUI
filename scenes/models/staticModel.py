from scenes.models.interfaces.model import SimpleModel, Updatable
from utils.debug import *

import numpy as np

class StaticModel(SimpleModel, Updatable):
    
    @timing
    def __init__(self, renderer, model, transform):
        super().__init__(renderer, model, transform)
        self.attach = None
    
    def __updateTranforms(self):
        attachFrame = self.attach.getFrame() if self.attach else np.identity(4)
        self.renderer.setTransformMatrix(self.modelId, np.matmul(attachFrame, self.transform))
        return
    
    def setAttach(self, iModel):
        self.attach = iModel
        self.__updateTranforms()
        return
    
    def setTransform(self, transform):
        self.transform = transform
        self.__updateTranforms()