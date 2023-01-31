from uiElement import *
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
            self.tabBtns.append(UiButton(self, constraints, Assets.TEST_SHADER))
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

{
    # def __init__(self, dim, title):
    #     self.dim = dim
    #     self.title = title
        
    #     self.clock = pygame.time.Clock()
    #     self.running = False

    #     self.sceneMap = {}

    #     self.scenes = [None]
    #     self.currentScene = None

    #     pygame.init()
    #     pygame.display.set_caption(self.title)
    #     self.screen = pygame.display.set_mode(self.dim,pygame.RESIZABLE)

    #     self.backgroundColor = (255, 200, 200)
    #     self.mousePos = (0,0)
    #     self.mouseButtons = [False] * 5
    #     self.keyState = {}

    #     self.uiEvents = []
    #     self.windowWrapper = UiWrapper(self, [], (0,0,*dim))
    #     self.tabHeight = 40

    # def createUi(self):
    #     self.tabButtons = []
    #     numBtn = len(self.scenes)
    #     padding = 10
    #     for i in range(numBtn):
    #         constraints = [
    #             ABSOLUTE(T_Y, padding),
    #             COMPOUND(RELATIVE(T_X, 1 / numBtn * i, P_W), ABSOLUTE(T_X, padding)),
    #             COMPOUND(RELATIVE(T_W, 1 / numBtn, P_W), ABSOLUTE(T_W, -2 * padding)),
    #             ABSOLUTE(T_H, self.tabHeight - 2 * padding)
    #         ]
    #         self.tabButtons.append(UiButton(self, constraints))
    #         self.tabButtons[-1].setText(self.scenes[i].name if self.scenes[i] else 'None')
    #         self.sceneMap[self.tabButtons[-1]] = self.scenes[i]
    #     self.windowWrapper.addChildren(*self.tabButtons)

    # def eventHandler(self):
    #     self.mousePos = pygame.mouse.get_pos()
    #     self.mouseButtons = pygame.mouse.get_pressed(num_buttons=5)
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             self.running = False
    #         if event.type == pygame.KEYDOWN:
    #             self.keyState[event.unicode] = True
    #         if event.type == pygame.KEYUP:
    #             self.keyState[event.unicode] = False
    #     for event in self.uiEvents:
    #         if event['action'] == 'release' and event['obj'] in self.tabButtons:
    #             self.currentScene = self.sceneMap[event['obj']]
    #         if self.currentScene: self.currentScene.eventHandler(event)
    #     self.uiEvents = []

    # def run(self):
    #     self.running = True
    #     while self.running:
            # timeDelta = self.clock.tick(60)/1000.0
            # self.eventHandler()
            # self.windowWrapper.update()
            # if(self.currentScene): self.currentScene.update(timeDelta)

            # self.screen.fill(self.backgroundColor)

            # self.windowWrapper.render()
            # if(self.currentScene): self.currentScene.render()
            
            # pygame.display.flip()
}
