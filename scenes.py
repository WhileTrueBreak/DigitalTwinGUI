from constraintManager import *
import scene

import pygame
import pygame_gui
from pygame_gui.elements import *

import random

from asyncua import Client, ua
import asyncio


class AirPScene(scene.Scene):
    
    def __init__(self, window, name, objId, id, opcua=None):
        super().__init__(window, name, opcua)
        self.objId = objId
        self.id = id

        self.localState = {}
        self.localState['btnlight'] = True
        self.localState['cl'] = True
        self.localState['dispindx'] = True
        self.localState['mode'] = 0
        self.localState['name'] = ''
        self.localState['pwr'] = True

        asyncio.run(self.syncOpcua())

    def createUi(self):
        mc = (self.uiManager, self.sceneContainer)

        self.btns = []
        self.btnMap = {
            'btnlight': 0,
            'cl': 1,
            'dispindx': 2,
            'mode': 3,
            'name': 4,
            'pwr': 5,
            'allergens': 6,
            'fltrstat0': 7,
            'fltrstat1': 8,
            'fltrstat2': 9,
            'pm25': 10,
        }
        btnPadding = 1
        btnCount = 11
        for i in range(btnCount):
            dim = self.cManager.calcConstraints(
                COMPOUND(RELATIVE(T_W, 0.25, P_W),ABSOLUTE(T_W, -btnPadding*2)),
                COMPOUND(RELATIVE(T_H, 1/btnCount, P_H), ABSOLUTE(T_H, -btnPadding*2)),
                COMPOUND(RELATIVE(T_X, 0.25, P_W), COMPOUND(RELATIVE(T_X, -1, T_W), ABSOLUTE(T_X, -btnPadding))),
                RELATIVE(T_Y, 1/btnCount*i, P_H)
            )
            self.btns.append(UIButton(pygame.Rect(*dim), f'btn{i}', *mc))
        self.sceneContainer.hide()
        return
    
    async def handleEventAsync(self, event):
        x=1

    def handleUiEvents(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btns[self.btnMap['pwr']]:
                self.localState['pwr'] = not self.localState['pwr']
        asyncio.run(self.handleEventAsync(event))
        return
    
    def updateVariables(self, delta):
        asyncio.run(self.updateOpcua())
    
    async def updateOpcua(self):
        await self.opcua.setValue(f'ns={self.objId};s=AP{self.id}c_BtnLight', self.localState['btnlight'], ua.VariantType.Boolean)
        self.btns[self.btnMap['btnlight']].set_text(f'{self.localState["btnlight"]}')
        await self.opcua.setValue(f'ns={self.objId};s=AP{self.id}c_CL', self.localState['cl'], ua.VariantType.Boolean)
        self.btns[self.btnMap['cl']].set_text(f'{self.localState["cl"]}')
        await self.opcua.setValue(f'ns={self.objId};s=AP{self.id}c_DisplayIndex', self.localState['dispindx'], ua.VariantType.Boolean)
        self.btns[self.btnMap['dispindx']].set_text(f'{self.localState["dispindx"]}')
        await self.opcua.setValue(f'ns={self.objId};s=AP{self.id}c_Mode', self.localState['mode'], ua.VariantType.Int32)
        self.btns[self.btnMap['mode']].set_text(f'{self.localState["mode"]}')
        await self.opcua.setValue(f'ns={self.objId};s=AP{self.id}c_Name', self.localState['name'], ua.VariantType.String)
        self.btns[self.btnMap['name']].set_text(f'{self.localState["name"]}')
        await self.opcua.setValue(f'ns={self.objId};s=AP{self.id}c_PWR', self.localState['pwr'], ua.VariantType.Boolean)
        self.btns[self.btnMap['pwr']].set_text(f'{self.localState["pwr"]}')
        
        value = await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}d_Allergens')
        self.btns[self.btnMap['allergens']].set_text(f'{value}')
        value = await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}d_FilterStatus0')
        self.btns[self.btnMap['fltrstat0']].set_text(f'{value}')
        value = await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}d_FilterStatus1')
        self.btns[self.btnMap['fltrstat1']].set_text(f'{value}')
        value = await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}d_FilterStatus2')
        self.btns[self.btnMap['fltrstat2']].set_text(f'{value}')
        value = await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}d_PM25')
        self.btns[self.btnMap['pm25']].set_text(f'{value}')
    
    async def syncOpcua(self):
        self.localState['btnlight'] =   await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}c_BtnLight')
        self.localState['cl']       =   await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}c_CL')
        self.localState['dispind']  =   await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}c_DisplayIndex')
        self.localState['mode']     =   await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}c_Mode')
        self.localState['name']     =   await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}c_Name')
        self.localState['pwr']      =   await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}c_PWR')
