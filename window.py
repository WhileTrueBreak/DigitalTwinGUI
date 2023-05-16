import pygame
from pygame.locals import *

import random

import time
from OpenGL import GL

from vectors import *
from math import *
import sys

from ui.elements.uiWrapper import UiWrapper
from ui.elements.uiButton import UiButton
from ui.elements.uiBlock import UiBlock
from ui.elements.ui3dScene import Ui3DScene
from ui.uiLayer import UiLayer

from utils.uiHelper import *
from ui.constraintManager import *
from asset import *

from constants import Constants

import ctypes

class Window():
    
    TAB_HEIGHT = 40

    def __init__(self, size, title, fullscreen=False, resizeable=False, vsync=True):
        pygame.init()
        display_flags = pygame.DOUBLEBUF | pygame.OPENGL
        if resizeable:
            display_flags = display_flags | pygame.RESIZABLE
        if fullscreen:
            display_flags = display_flags | pygame.FULLSCREEN
            size = (0,0)
        self.screen = pygame.display.set_mode(size, display_flags, vsync=(1 if vsync else 0))
        pygame.display.set_caption(title)

        self.dim = self.screen.get_size()
        self.ogdim = self.dim

        self.initOpenGL()

        self.delta = 1

        self.running = True
        self.initialize()

    def initOpenGL(self):
        GL.glEnable(GL.GL_BLEND)
        GL.glCullFace(GL.GL_BACK)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glViewport(0, 0, self.dim[0], self.dim[1]) # Set viewport
        GL.glEnable(GL.GL_DEPTH_TEST) # Enable depth testing
        GL.glClearColor(0,0,0,1)
        GL.glDepthFunc(GL.GL_LESS)

        Constants.MAX_TEXTURE_SLOTS = GL.glGetIntegerv(GL.GL_MAX_TEXTURE_IMAGE_UNITS)

    def initialize(self):
        self.timeCounter = 0
        self.frames = 0
        self.resized = False

        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glEnable(GL.GL_BLEND)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glCullFace(GL.GL_BACK)

        self.uiEvents = []
        self.mousePos = (0,0)
        self.mouseButtons = [False]*5
        self.keyState = {}

        self.uiSelectBuffer = []
        self.selectedUi = None

        self.scenes = []
        self.sceneName = []
        self.sceneMap = {}
        self.currentScene = None

        self.uiLayer = UiLayer(self)

        Assets.init()
    
    def createUi(self):

        constraints = [ABSOLUTE(T_X, 0),
                       ABSOLUTE(T_Y, 0),
                       RELATIVE(T_W, 1, P_W),
                       ABSOLUTE(T_H, 40)]
        self.tabWrapper = UiWrapper(self, constraints)
        self.uiLayer.getMasterElem().addChild(self.tabWrapper)
        constraints = [ABSOLUTE(T_X, 0),
                       ABSOLUTE(T_Y, 40),
                       RELATIVE(T_W, 1, P_W),
                       COMPOUND(RELATIVE(T_H, 1, P_H), ABSOLUTE(T_H, 40))]
        self.sceneWrapper = UiWrapper(self, constraints)
        self.uiLayer.getMasterElem().addChild(self.sceneWrapper)

        self.tabBtns = []
        numBtns = len(self.scenes)
        
        for i in range(numBtns):
            constraints = [
                COMPOUND(RELATIVE(T_Y, -0.5, T_H), RELATIVE(T_Y, 0.5, P_H)),
                COMPOUND(RELATIVE(T_X, -0.5, T_W), RELATIVE(T_X, 0.5/numBtns + 1/numBtns * i, P_W)),
                RELATIVE(T_H, 0.9, P_H),
                COMPOUND(RELATIVE(T_W, 1/numBtns, P_W), RELATIVE(T_W, -0.1, P_H))
            ]

            btn, text = centeredTextButton(self, constraints)
            text.setText(f'{self.sceneName[i]}')
            text.setFontSize(24)
            text.setTextSpacing(6)
            text.setTextColor((1,1,1))
            text.setFont(Assets.ARIAL_FONT)
            btn.setDefaultColor([0,109/255,174/255])
            btn.setHoverColor([0,159/255,218/255])
            btn.setPressColor([0,172/255,62/255])
            self.sceneMap[btn] = self.scenes[i]
            self.tabBtns.append(btn)
        self.tabWrapper.addChildren(*self.tabBtns)

    def __createModels(self):
        self.modelRenderer.setViewMatrix(createViewMatrix(-0.7+5, -0.57+2, 1.5, -70.25, 0, 45))
        self.benches = [0]*5
        self.benches[0] = self.modelRenderer.addModel(Assets.TABLES[1], createTransformationMatrix(7-0.4, 0.8+1.05, 0.85, 0, 0, 0))
        self.benches[1] = self.modelRenderer.addModel(Assets.TABLES[1], createTransformationMatrix(7-1.05, 0.4, 0.85, 0, 0, 90))
        self.benches[2] = self.modelRenderer.addModel(Assets.TABLES[2], createTransformationMatrix(7-0.9, 0.8+2.1+0.9, 0.85, 0, 0, 0))
        self.benches[3] = self.modelRenderer.addModel(Assets.KUKA_BASE, createTransformationMatrix(7-0.9-0.7, 0.8+2.1+0.9-1.6, 0.85+0.06625, 0, 0, 0))
        self.benches[3] = self.modelRenderer.addModel(Assets.KUKA_BASE, createTransformationMatrix(7-1, 0.8+2.1+1.8+0.6, 0.85+0.06625, 0, 0, 0))

    def getMousePos(self):
        return self.mousePos
    
    def getMouseState(self, button):
        return self.mouseButtons[button]

    def getKeyState(self, key):
        if not key in self.keyState:
            return False
        return self.keyState[key]

    def eventHandler(self):
        cResized = False
        self.mousePos = pygame.mouse.get_pos()
        self.mouseButtons = pygame.mouse.get_pressed(num_buttons=5)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                if self.currentScene != None:
                    self.uiLayer.getMasterElem().removeChild(self.currentScene.sceneWrapper)
                    self.currentScene.stop()
            elif event.type == pygame.VIDEORESIZE:
                cResized = True
            elif event.type == pygame.KEYDOWN:
                self.keyState[event.key] = True
            elif event.type == pygame.KEYUP:
                self.keyState[event.key] = False
        if cResized:
            self.updateWindow()
            self.resized = True
        elif not cResized:
            self.resized = False
        for event in self.uiEvents:
            if event['action'] == 'release' and event['obj'] in self.tabBtns:
                if self.currentScene != None:
                    self.uiLayer.getMasterElem().removeChild(self.currentScene.sceneWrapper)
                    self.currentScene.stop()
                self.currentScene = self.sceneMap[event['obj']]
                if self.currentScene != None:
                    self.uiLayer.getMasterElem().addChild(self.currentScene.sceneWrapper)
                    self.currentScene.start()
            if self.currentScene: self.currentScene.eventHandler(event)
        self.selectedUi = self.uiSelectBuffer[0] if len(self.uiSelectBuffer) > 0 else self.selectedUi
        self.uiSelectBuffer = []
        self.uiEvents = []

    def updateWindow(self):
        self.dim = pygame.display.get_window_size()
        return

    def update(self):
        self.eventHandler()
        if self.currentScene != None:
            self.currentScene.update(self.delta)
        self.uiLayer.update(self.delta)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        self.uiLayer.render()
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
                print(f'frame time: {1000000/self.frames:.0f}us | FPS: {self.frames}')
                self.timeCounter -= 1
                self.frames = 0
        if self.currentScene != None:
            self.currentScene.stop() 
        pygame.quit()
        sys.exit()

    def addScene(self, scene):
        scene.sceneWrapper.updateXPos(ABSOLUTE(T_X, 0))
        scene.sceneWrapper.updateYPos(ABSOLUTE(T_Y, 40))
        scene.sceneWrapper.updateWidth(RELATIVE(T_W, 1, P_W))
        scene.sceneWrapper.updateHeight(COMPOUND(RELATIVE(T_H, 1, P_H), ABSOLUTE(T_H, -40)))
        self.scenes.append(scene)
        self.sceneName.append(scene.name)

    def getWindowScale(self):
        return (self.dim[0]/self.ogdim[0],self.dim[1]/self.ogdim[1])

    def getHoveredUI(self):
        data = self.uiLayer.getScreenSpaceUI(*self.getMousePos())
        return data
