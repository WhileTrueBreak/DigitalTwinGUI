from abc import abstractmethod
import numpy as np

from utils.mathHelper import getFrustum, pointFrustumDist
from window import Window

class SimpleModel:
    
    def __init__(self, renderer, model, transform):
        self.renderer = renderer
        self.transform = transform
        self.model = model
        self.modelId = self.renderer.addModel(model, transform)

        self.inView = True
        self.viewCheckFrame = -1
    
    def getFrame(self):
        return self.transform

    def isModel(self, modelId):
        return modelId == self.modelId
    
    def inViewFrustrum(self, proj, view):
        if self.viewCheckFrame == Window.INSTANCE.frameCount: return self.inView

        aabbBound = self.model.getAABBBound(self.transform)
        frustum = getFrustum(np.matmul(proj.T,view))
        dists = np.matmul(aabbBound, frustum.T)

        self.inView = not np.any(np.all(dists < 0, axis=0))
        self.viewCheckFrame = Window.INSTANCE.frameCount
        return self.inView

    def setViewFlag(self, flag):
        self.renderer.setViewFlag(self.modelId, flag)

class Updatable:

    @abstractmethod
    def update(self, delta):
        ...

    @abstractmethod
    def setAttach(self, iModel):
        ...
    
    @abstractmethod
    def setTransform(self, mat):
        ...
    