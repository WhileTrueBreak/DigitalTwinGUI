from ui.uiElement import *
from ui.uiHelper import *
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

from asset import *

class Window():
    
    TAB_HEIGHT = 40

    def __init__(self, size, title):
        pygame.init()
        display_flags = pygame.DOUBLEBUF | pygame.OPENGL
        self.screen = pygame.display.set_mode(size, display_flags)
        pygame.display.set_caption(title)

        self.dim = self.screen.get_size()

        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glEnable(GL.GL_BLEND)
        GL.glCullFace(GL.GL_BACK)
        GL.glClearColor(1, 1, 1, 1)

        self.delta = 1

        self.running = True
        self.initialize()
    
    def initialize(self):
        self.timeCounter = 0
        self.frames = 0

        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA);  
        GL.glEnable(GL.GL_BLEND)
        GL.glCullFace(GL.GL_BACK)
        GL.glClearColor(0.5, 0.5, 0.5, 1)

        self.uiEvents = []
        self.mousePos = (0,0)
        self.mouseButtons = [False]*5
        self.keyState = {}

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
            # btn = UiButton(self, constraints, Assets.SOLID_SHADER)
            btn, text = centeredTextButton(self, constraints, Assets.SOLID_SHADER)
            text.setText(f'{self.scenes[i].name if self.scenes[i] != None else "None"}')
            text.setFontSize(24)
            text.setTextSpacing(15)
            text.setTextColor((0,0,0))
            self.tabBtns.append(btn)
            self.tabBtns[-1].setColor([1.0,0.8,0.8])
            self.sceneMap[self.tabBtns[-1]] = self.scenes[i]
        self.tabWrapper.addChildren(*self.tabBtns)

    def getKeyState(self, key):
        if not key in self.keyState:
            return False
        return self.keyState[key]

    def eventHandler(self):
        self.mousePos = pygame.mouse.get_pos()
        self.mouseButtons = pygame.mouse.get_pressed(num_buttons=5)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                if self.currentScene != None:
                    self.windowWrapper.removeChild(self.currentScene.sceneWrapper)
                    self.currentScene.stop()
            if event.type == pygame.KEYDOWN:
                self.keyState[event.key] = True
            if event.type == pygame.KEYUP:
                self.keyState[event.key] = False
        for event in self.uiEvents:
            if event['action'] == 'release' and event['obj'] in self.tabBtns:
                if self.currentScene != None:
                    self.windowWrapper.removeChild(self.currentScene.sceneWrapper)
                    self.currentScene.stop()
                self.currentScene = self.sceneMap[event['obj']]
                if self.currentScene != None:
                    self.windowWrapper.addChild(self.currentScene.sceneWrapper)
                    self.currentScene.start()
            if self.currentScene: self.currentScene.eventHandler(event)
        self.uiEvents = []

    def update(self):
        self.eventHandler()
        if self.currentScene != None:
            self.currentScene.update(self.delta)
        self.windowWrapper.update(self.delta)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT|GL.GL_DEPTH_BUFFER_BIT)
        self.windowWrapper.render()
        return

    def run(self):
        start = time.time_ns()
        while self.running:
            end = start
            start = time.time_ns()

            self.update()

            pygame.display.flip()

            self.delta = (start - end)/1000000000
            self.timeCounter += self.delta
            self.frames += 1
            if self.timeCounter >= 1:
                print(f'frame time: {1/self.frames:.2f} | FPS: {self.frames}')
                self.timeCounter -= 1
                self.frames = 0
        pygame.quit()
        sys.exit()


