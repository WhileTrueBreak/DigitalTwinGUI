from abc import abstractmethod

class IModel:

    @abstractmethod
    def update(self):
        ...

    @abstractmethod
    def handleEvents(self):
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