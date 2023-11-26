from abc import abstractmethod

class SimpleModel:
    
    def __init__(self, renderer, model, transform):
        self.renderer = renderer
        self.transform = transform
        self.modelId = self.renderer.addModel(model, transform)
    
    def isModel(self, modelId):
        return modelId == self.modelId

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
    