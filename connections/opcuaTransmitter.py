from connections.opcua import *

class OpcuaTransmitter:
    def __init__(self, container, host):
        self.container = container
        self.host = host
        self.threadStopFlag = False
        self.thread = None
    
    def start(self):
        self.threadStopFlag = False
        if self.thread == None or not self.thread.is_alive():
            self.thread = Opcua.createOpcuaTransmitterThread(self.container, self.host, lambda:self.threadStopFlag)

    def stop(self):
        self.threadStopFlag = True