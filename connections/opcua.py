from asyncua import Client
import asyncio

import time

from threading import Thread

class OpcuaContainer:
    def __init__(self):
        self.updated = {}
        self.opcuaDict = {}
    
    def getValue(self, key, default=None):
        if not key in self.opcuaDict: return (default, 0)
        self.updated[key] = False
        return self.opcuaDict[key]
    
    def setValue(self, key, value, type):
        self.updated[key] = True
        self.opcuaDict[key] = (value, type)
    
    def hasUpdated(self, key):
        if not key in self.opcuaDict: return False
        return self.updated[key]

class Opcua:

    MAX_POLLING_RATE = 30

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
            # print(f'added {node} to dict for {self.__class__.__name__}')
            return await self.nodeDict[node].set_value(value, type)
        except Exception:
            raise Exception(f'Error setting value')

    async def getValue(self, node):
        try:
            if node in self.nodeDict:
                return (await self.nodeDict[node].get_value(), await self.nodeDict[node].read_data_type_as_variant_type())
            self.nodeDict[node] = self.opcuaClient.get_node(node)
            # print(f'added {node} to dict for {self}')
            return (await self.nodeDict[node].get_value(), await self.nodeDict[node].read_data_type_as_variant_type())
        except Exception:
            raise Exception(f'Error getting value')
    @staticmethod
    def createOpcuaReceiverThread(container, host, data, stop):
        t = Thread(target = Opcua.opcuaReceiverConnection, args =(container, host, data, stop))
        t.start()
        return t
    @staticmethod
    def opcuaReceiverConnection(container, host, data, stop):
        # print(f'Opcua receiver thread started: {host}')
        start = time.time_ns()
        delay = 1/Opcua.MAX_POLLING_RATE*1000000000
        try:
            client = Opcua(host)
        except:
            stop = lambda:True
        rate = 0
        accum = 0
        while not stop():
            start = time.time_ns()
            try:
                asyncio.run(Opcua.OpcuaGetData(container, data, client))
            except:
                return
            time_past = time.time_ns() - start
            time.sleep(max(0, (delay-time_past)/1000000000))
            rate += 1
            accum += time.time_ns() - start
            if accum >= 10000000000:
                # print(f'Opcua receiver polling rate: {int(rate/10)}/s')
                accum -= 10000000000
                rate = 0
        # print(f'Opcua receiver thread stopped: {host}')
    @staticmethod
    async def OpcuaGetData(container, data, client):
        for d in data:
            container.setValue(d, *(await client.getValue(d)))
    @staticmethod
    def createOpcuaTransmitterThread(container, host, stop):
        t = Thread(target = Opcua.opcuaTransmitterConnection, args =(container, host, stop))
        t.start()
        return t
    @staticmethod
    def opcuaTransmitterConnection(container, host, stop):
        # print(f'Opcua transmitter thread started: {host}')
        try:
            client = Opcua(host)
        except:
            stop = lambda:True
        start = time.time_ns()
        delay = 1/Opcua.MAX_POLLING_RATE*1000000000
        rate = 0
        accum = 0
        while not stop():
            start = time.time_ns()
            try:
                for key in container.opcuaDict:
                    if not container.hasUpdated(key): continue
                    v,t = container.getValue(key)
                    asyncio.run(client.setValue(key, v, t))
            except:
                return
            time_past = time.time_ns() - start
            time.sleep(max(0, (delay-time_past)/1000000000))
            rate += 1
            accum += time.time_ns() - start
            if accum >= 10000000000:
                # print(f'Opcua transmitter polling rate: {int(rate/10)}/s')
                accum -= 10000000000
                rate = 0
        # print(f'Opcua transmitter thread stopped: {host}')





