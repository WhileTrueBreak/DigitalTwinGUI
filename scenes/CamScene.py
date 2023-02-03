from ui.uiElement import *
from ui.uiHelper import *
from constraintManager import *
from scenes.scene import *

import pygame

import random

from asyncua import Client, ua
import asyncio
import asyncio

class CamScene(Scene):
    
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
        btn, text = centeredTextButton(self.window, constraints, Assets.SOLID_SHADER)
        btn.setColor((1,1,1))
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
        btn, text = centeredTextButton(self.window, constraints, Assets.SOLID_SHADER)
        btn.setColor((1,1,1))
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
    
    def absUpdate(self, delta):
        return

    def start(self):
        ...
    
    def stop(self):
        return


