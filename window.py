from uiElement import *
from uiHelper import *
from constraintManager import *

import pygame

import time
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import matplotlib.cm
from vectors import *
from math import *

from py3d.core.base import Base
from py3d.core.utils import Utils
from py3d.core.attribute import Attribute
from py3d.core.uniform import Uniform
from asset import *

class Window(Base):
    
    TAB_HEIGHT = 40
    
    def initialize(self):
        self.dim = self._screen.get_size()

        self.uiEvents = []
        self.mousePos = (0,0)
        self.mouseButtons = [False]*5

        self.scenes = [None]
        self.sceneMap = {}
        self.currentScene = None

        Assets.init()
    
    def createUi(self):
        self.windowWrapper = UiWrapper(self, [], (0,0,self.dim[0], self.dim[1]))
        
        constraints = [
            ABSOLUTE(T_X, 0),
            ABSOLUTE(T_Y, 0),
            RELATIVE(T_W, 1, P_W),
            ABSOLUTE(T_H, 40),
        ]
        self.tabWrapper = UiWrapper(self, constraints)
        self.windowWrapper.addChild(self.tabWrapper)

        self.tabBtns = []
        numBtns = len(self.scenes)
        for i in range(numBtns):
            constraints = [
                COMPOUND(RELATIVE(T_Y, -0.5, T_H), RELATIVE(T_Y, 0.5, P_H)),
                COMPOUND(RELATIVE(T_X, -0.5, T_W), RELATIVE(T_X, 0.5/numBtns + 1/numBtns * i, P_W)),
                RELATIVE(T_H, 0.9, P_H),
                COMPOUND(RELATIVE(T_W, 1/numBtns, P_W), RELATIVE(T_W, -0.1, P_H))
            ]
            btn, text = centeredTextButton(self, constraints, Assets.TEST_SHADER)
            text.setText(f'{self.scenes[i].name if self.scenes[i] != None else "None"}')
            text.setFontSize(24)
            text.setTextSpacing(15)
            text.setTextColor((0,0,0))
            self.tabBtns.append(btn)
            self.tabBtns[-1].setColor([1.0,0.8,0.8])
            self.sceneMap[self.tabBtns[-1]] = self.scenes[i]
        self.tabWrapper.addChildren(*self.tabBtns)

    def eventHandler(self):
        self.mousePos = pygame.mouse.get_pos()
        self.mouseButtons = pygame.mouse.get_pressed(num_buttons=5)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                self.keyState[event.unicode] = True
            if event.type == pygame.KEYUP:
                self.keyState[event.unicode] = False
        for event in self.uiEvents:
            if event['action'] == 'release' and event['obj'] in self.tabBtns:
                if self.currentScene != None:
                    self.windowWrapper.removeChild(self.currentScene.sceneWrapper)
                self.currentScene = self.sceneMap[event['obj']]
                if self.currentScene != None:
                    self.windowWrapper.addChild(self.currentScene.sceneWrapper)
            if self.currentScene: self.currentScene.eventHandler(event)
        self.uiEvents = []

    def update(self):
        self.eventHandler()
        if self.currentScene != None:
            self.currentScene.update()
        self.windowWrapper.update()
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        self.windowWrapper.render()
        return




