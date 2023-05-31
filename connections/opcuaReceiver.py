from connections.opcua import *

class OpcuaReceiver:
    def __init__(self, data, container, host):
        self.data = data
        self.container = container
        self.host = host
        self.threadStopFlag = False
        self.thread = None
    
    def start(self):
        self.threadStopFlag = False
        if self.thread == None or not self.thread.is_alive():
            self.thread = Opcua.createOpcuaReceiverThread(self.container, self.host, self.data, lambda:self.threadStopFlag)

    def stop(self):
        self.threadStopFlag = True