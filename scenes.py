import scene

import pygame
import pygame_gui
from pygame_gui.elements import *

import random

from syncer import sync
from asyncua import Client, ua
import asyncio

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

class Opcua:
    def __init__(self):
        self.OpcUaHost = 'oct.tpc://172.31.1.236:4840/server/'
        self.opcuaClient = Client(self.OpcUaHost)
        asyncio.run(self.opcuaClient.connect())
        self.nodeDict = {}

    async def sendValue(self, node, value, type):
        try:
            if node in self.nodeDict:
                await self.nodeDict[node].set_value(value, type)
            self.nodeDict[node] = self.opcuaClient.get_node(node)
            print(f'added {node} to dict')
        except Exception:
            print(f'Error setting value:\n{traceback.print_exc()}')

    async def getValue(self, node):
        try:
            if node in self.nodeDict:
                return await self.nodeDict[node].get_value()
            self.nodeDict[node] = self.opcuaClient.get_node(node)
            print(f'added {node} to dict')
            return await self.nodeDict[node].get_value()
        except Exception:
            print(f'Error getting value:\n{traceback.print_exc()}')

class AirPScene(scene.Scene):
    
    def __init__(self, window, name, objId, id):
        super().__init__(window, name)
        self.opcua = Opcua()
        self.objId = objId
        self.id = id

    def createUi(self):
        self.pwrbtn = UIButton(pygame.Rect((int(self.dim[0] / 4), int(self.dim[1] / 4)),(int(self.dim[0] / 2), int(self.dim[1] / 2))),
                           'Power',
                           self.uiManager)
        return
    
    def handleUiEvents(self, event):
        
        return
    
    def updateVariables(self, delta):
        loop = get_or_create_eventloop()
        loop.run_until_complete(asyncio.gather(self.updateOpcua(), return_exceptions=True))
        
    @sync
    async def updateOpcua(self):
        value = await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}c_PWR')
        self.pwrbtn.set_text(f'{value}')
