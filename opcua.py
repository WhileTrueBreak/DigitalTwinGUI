from asyncua import Client, ua
import asyncio

from threading import Thread

class Opcua:
    def __init__(self):
        self.OpcUaHost = 'oct.tpc://172.31.1.236:4840/server/'
        self.opcuaClient = Client(self.OpcUaHost)
        asyncio.run(self.opcuaClient.connect())
        self.nodeDict = {}

    async def setValue(self, node, value, type):
        try:
            if node in self.nodeDict:
                return await self.nodeDict[node].set_value(value, type)
            self.nodeDict[node] = self.opcuaClient.get_node(node)
            print(f'added {node} to dict')
            return await self.nodeDict[node].set_value(value, type)
        except Exception:
            raise Exception(f'Error setting value')

    async def getValue(self, node):
        try:
            if node in self.nodeDict:
                return await self.nodeDict[node].get_value()
            self.nodeDict[node] = self.opcuaClient.get_node(node)
            print(f'added {node} to dict')
            return await self.nodeDict[node].get_value()
        except Exception:
            raise Exception(f'Error getting value')
    @staticmethod
    def createOpcuaThread(q, data, stop):
        t = Thread(target = Opcua.opcuaConnection, args =(q, data, stop))
        t.start()
        return t
    @staticmethod
    def opcuaConnection(q, data, stop):
        print('')
        client = Opcua()
        while not stop():
            asyncio.run(Opcua.OpcuaGetData(q, data, client))
    @staticmethod
    async def OpcuaGetData(q, data, client):
        ddict = {}
        for d in data:
            ddict[d] = await client.getValue(d)
        q.put(ddict)
    






