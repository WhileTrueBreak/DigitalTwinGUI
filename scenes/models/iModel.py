from abc import abstractmethod

class IModel:

    @abstractmethod
    def update(self, delta):
        ...

    @abstractmethod
    def handleEvents(self, event):
        ...

    @abstractmethod
    def start(self):
        ...

    @abstractmethod
    def stop(self):
        ...

    @abstractmethod
    def getControlPanel(self):
        ...

    @abstractmethod
    def isModel(self):
        ...
    
    @abstractmethod
    def setAttach(self, iModel):
        ...
    
    @abstractmethod
    def setTransform(self, mat):
        ...
    