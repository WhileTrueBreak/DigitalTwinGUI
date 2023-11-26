from abc import abstractmethod

class PollController:

    @abstractmethod
    def start(self):
        ...

    @abstractmethod
    def stop(self):
        ...
