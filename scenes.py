from uiElement import *
from uiHelper import *
from constraintManager import *
import scene

import pygame

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

        self.btns = []
        self.btnMap = {
            'btnlight': 3,
            'cl': 5,
            'dispindx': 4,
            'mode': 2,
            'name': 0,
            'pwr': 1,
            'allergens': 7,
            'fltrstat0': 8,
            'fltrstat1': 9,
            'fltrstat2': 10,
            'pm25': 6,
        }
        btnPadding = 5
        btnCount = 11
        for i in range(btnCount):
            constraints = [
                COMPOUND(RELATIVE(T_W, 0.25, P_W),ABSOLUTE(T_W, -btnPadding*2)),
                COMPOUND(RELATIVE(T_H, 1/btnCount, P_H), ABSOLUTE(T_H, -btnPadding*2)),
                COMPOUND(RELATIVE(T_X, 0.25, P_W), COMPOUND(RELATIVE(T_X, -1, T_W), ABSOLUTE(T_X, -btnPadding))),
                RELATIVE(T_Y, 1/btnCount*i, P_H)
            ]
            self.btns.append(UiButton(self.window, constraints))
        
        self.sceneWrapper.addChildren(*self.btns)

    def handleUiEvents(self, event):
        if event['action'] == 'release':
            if event['obj'] == self.btns[self.btnMap['btnlight']]:
                self.localState['btnlight'] = not self.localState['btnlight']
            if event['obj'] == self.btns[self.btnMap['cl']]:
                self.localState['cl'] = not self.localState['cl']
            if event['obj'] == self.btns[self.btnMap['dispindx']]:
                self.localState['dispindx'] = not self.localState['dispindx']
            if event['obj'] == self.btns[self.btnMap['pwr']]:
                self.localState['pwr'] = not self.localState['pwr']
            if event['obj'] == self.btns[self.btnMap['mode']]:
                self.localState['mode'] = (self.localState['mode']+1)%4
        return
    
    def updateVariables(self):
        asyncio.run(self.updateOpcua())
    
    async def updateOpcua(self):
        await self.opcua.setValue(f'ns={self.objId};s=AP{self.id}c_BtnLight', self.localState['btnlight'], ua.VariantType.Boolean)
        self.btns[self.btnMap['btnlight']].setText(f'btn lights: {"on" if self.localState["btnlight"] else "off"}')
        await self.opcua.setValue(f'ns={self.objId};s=AP{self.id}c_CL', self.localState['cl'], ua.VariantType.Boolean)
        self.btns[self.btnMap['cl']].setText(f'child lock: {"on" if self.localState["cl"] else "off"}')
        await self.opcua.setValue(f'ns={self.objId};s=AP{self.id}c_DisplayIndex', self.localState['dispindx'], ua.VariantType.Boolean)
        self.btns[self.btnMap['dispindx']].setText(f'display index: {"IAI" if self.localState["dispindx"] else "PM25"}')
        await self.opcua.setValue(f'ns={self.objId};s=AP{self.id}c_Mode', self.localState['mode'], ua.VariantType.Int32)
        self.btns[self.btnMap['mode']].setText(f'mode: {self.localState["mode"]}')
        await self.opcua.setValue(f'ns={self.objId};s=AP{self.id}c_Name', self.localState['name'], ua.VariantType.String)
        self.btns[self.btnMap['name']].setText(f'name: {self.localState["name"]}')
        await self.opcua.setValue(f'ns={self.objId};s=AP{self.id}c_PWR', self.localState['pwr'], ua.VariantType.Boolean)
        self.btns[self.btnMap['pwr']].setText(f'power: {"on" if self.localState["pwr"] else "off"}')
        
        value = await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}d_Allergens')
        self.btns[self.btnMap['allergens']].setText(f'allergens: {value}')
        value = await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}d_FilterStatus0')
        self.btns[self.btnMap['fltrstat0']].setText(f'filter status 1: {value} hours')
        value = await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}d_FilterStatus1')
        self.btns[self.btnMap['fltrstat1']].setText(f'filter status 0: {value} hours')
        value = await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}d_FilterStatus2')
        self.btns[self.btnMap['fltrstat2']].setText(f'filter status 2: {value} hours')
        value = await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}d_PM25')
        self.btns[self.btnMap['pm25']].setText(f'PM25: {value}')
    
    async def syncOpcua(self):
        self.localState['btnlight'] =   await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}c_BtnLight')
        self.localState['cl']       =   await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}c_CL')
        self.localState['dispindx']  =   await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}c_DisplayIndex')
        self.localState['mode']     =   await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}c_Mode')
        self.localState['name']     =   await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}c_Name')
        self.localState['pwr']      =   await self.opcua.getValue(f'ns={self.objId};s=AP{self.id}c_PWR')

class CamScene(scene.Scene):
    
    def __init__(self, window, name):
        super().__init__(window, name)
        self.isDisplayed = False
        self.camBtns = []
        self.streams = []

    def createUi(self):
        btnPadding = 5
        constraints = [
            COMPOUND(RELATIVE(T_X, 0, P_W), ABSOLUTE(T_X, btnPadding)),
            ABSOLUTE(T_Y, btnPadding),
            COMPOUND(RELATIVE(T_W, 0.25, P_W), ABSOLUTE(T_W, -2 * btnPadding)),
            ABSOLUTE(T_H, 30)
        ]
        btn, text = centeredTextButton(self.window, constraints, Assets.TEST_SHADER)
        text.setText('stream 1')
        text.setFontSize(24)
        text.setTextSpacing(15)
        text.setTextColor((0,0,0))
        self.camBtns.append(btn)

        constraints = [
            COMPOUND(RELATIVE(T_X, 0, P_W), ABSOLUTE(T_X, btnPadding)),
            COMPOUND(ABSOLUTE(T_Y, 30 + 2 * btnPadding), ABSOLUTE(T_Y, btnPadding)),
            COMPOUND(RELATIVE(T_W, 0.25, P_W), ABSOLUTE(T_W, -2 * btnPadding)),
            ABSOLUTE(T_H, 30)
        ]
        btn, text = centeredTextButton(self.window, constraints, Assets.TEST_SHADER)
        text.setText('stream 2')
        text.setFontSize(24)
        text.setTextSpacing(15)
        text.setTextColor((0,0,0))
        self.camBtns.append(btn)

        constraints = [
            COMPOUND(RELATIVE(T_X, 0.5, P_W), ABSOLUTE(T_X, btnPadding)),
            ABSOLUTE(T_Y, btnPadding),
            COMPOUND(RELATIVE(T_W, 0.5, P_W), ABSOLUTE(T_W, -2 * btnPadding)),
            RELATIVE(T_H, 3/4, T_W)
        ]
        self.streams.append(UiStream(self.window, constraints, 'http://172.31.1.225:8080/?action=streams'))
        self.streams.append(UiStream(self.window, constraints, 'http://172.31.1.226:8080/?action=streams'))
        self.sceneWrapper.addChildren(*self.camBtns)

    def handleUiEvents(self, event):
        if event['action'] == 'release':
            for i in range(len(self.streams)):
                if event['obj'] != self.camBtns[i]: continue
                self.sceneWrapper.removeChildren(*self.streams)
                self.sceneWrapper.addChild(self.streams[i])
        return
    
    def updateVariables(self):
        return
