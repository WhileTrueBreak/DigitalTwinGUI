from connections.opcua import *

class OpcuaTransmitter:
    def __init__(self, container, host, pollingRate=30):
        self.container = container
        self.host = host
        self.threadStopFlag = False
        self.thread = None
        self.pollingRate = pollingRate
    
    def start(self):
        self.threadStopFlag = False
        if self.thread == None or not self.thread.is_alive():
            self.thread = Opcua.createOpcuaTransmitterThread(self.container, self.host, lambda:self.threadStopFlag, pollingRate=self.pollingRate)

    def stop(self):
        self.threadStopFlag = True