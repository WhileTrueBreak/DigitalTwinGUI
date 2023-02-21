from asyncua import Client
import asyncio

import time

from threading import Thread

class OpcuaContainer:
    def __init__(self):
        self.updated = False
        self.opcuaDict = {}
    
    def getValue(self, key, default=None):
        if not key in self.opcuaDict: return default
        return self.opcuaDict[key]
    
    def setValue(self, key, value):
        self.updated = True
        self.opcuaDict[key] = value
    
    def hasUpdated(self):
        return self.updated

class Opcua:
    def __init__(self, host):
        self.OpcUaHost = host #'oct.tpc://172.31.1.236:4840/server/'
        self.opcuaClient = Client(self.OpcUaHost)
        asyncio.run(self.opcuaClient.connect())
        self.nodeDict = {}

    async def setValue(self, node, value, type):
        try:
            if node in self.nodeDict:
                return await self.nodeDict[node].set_value(value, type)
            self.nodeDict[node] = self.opcuaClient.get_node(node)
            print(f'added {node} to dict for {self}')
            return await self.nodeDict[node].set_value(value, type)
        except Exception:
            raise Exception(f'Error setting value')

    async def getValue(self, node):
        try:
            if node in self.nodeDict:
                return await self.nodeDict[node].get_value()
            self.nodeDict[node] = self.opcuaClient.get_node(node)
            print(f'added {node} to dict for {self}')
            return await self.nodeDict[node].get_value()
        except Exception:
            raise Exception(f'Error getting value')
    @staticmethod
    def createOpcuaThread(container, host, data, stop):
        t = Thread(target = Opcua.opcuaConnection, args =(container, host, data, stop))
        t.start()
        return t
    @staticmethod
    def opcuaConnection(container, host, data, stop):
        print(f'Opcua thread started: {host}')
        try:
            client = Opcua(host)
        except:
            stop = lambda:True
        while not stop():
            time.sleep(0.01)
            try:
                asyncio.run(Opcua.OpcuaGetData(container, data, client))
            except:
                return
        print(f'Opcua thread stopped: {host}')
    @staticmethod
    async def OpcuaGetData(container, data, client):
        for d in data:
            container.setValue(d, await client.getValue(d))
    






