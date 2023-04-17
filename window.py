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
from ui.uiLayer import UiLayer

from utils.uiHelper import *
from constraintManager import *
from asset import *

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
        GL.glClearColor(0.0, 0.0, 0.0, 1.0) # Set clear color
        GL.glViewport(0, 0, self.dim[0], self.dim[1]) # Set viewport
        GL.glEnable(GL.GL_DEPTH_TEST) # Enable depth testing
        GL.glDepthFunc(GL.GL_LESS)

    def initialize(self):
        self.timeCounter = 0
        self.frames = 0
        self.resized = False

        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glEnable(GL.GL_BLEND)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glCullFace(GL.GL_BACK)
        GL.glClearColor(0, 0, 0, 1)

        self.uiEvents = []
        self.mousePos = (0,0)
        self.mouseButtons = [False]*5
        self.keyState = {}

        self.uiSelectBuffer = []
        self.selectedUi = None

        self.scenes = [None, None, None, None, None, None]
        self.text = ['a', 'b', 'c', 'd', 'e', 'f']
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
            # text.setText(f'{self.scenes[i].name if self.scenes[i] != None else "None"}')
            text.setText(f'{self.text[i]}')
            text.setFontSize(24)
            text.setTextSpacing(7)
            text.setTextColor((0,0,0))
            btn.setDefaultColor([1.0,0.8,0.8])
            btn.setHoverColor([1.0,0.7,0.7])
            btn.setPressColor([1.0,0.6,0.6])
            self.sceneMap[btn] = self.scenes[i]
            self.tabBtns.append(btn)
        self.tabWrapper.addChildren(*self.tabBtns)


        t = UiBlock(self, [
            *Constraints.ALIGN_CENTER,RELATIVE(T_W, 0.8, P_W), RELATIVE(T_H, 0.9, P_H)
            ])
        t.setTexture(Assets.CUBE_TEX.getTexture())
        t.setColor([1,1,1])
        self.uiLayer.getMasterElem().addChild(t)

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
                    self.windowWrapper.removeChild(self.currentScene.sceneWrapper)
                    self.currentScene.stop()
            elif event.type == pygame.VIDEORESIZE:
                cResized = True
            elif event.type == pygame.KEYDOWN:
                self.keyState[event.key] = True
            elif event.type == pygame.KEYUP:
                self.keyState[event.key] = False
        if not cResized and self.resized:
            self.updateWindow()
            self.resized = False
        elif cResized:
            self.resized = True
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
        self.selectedUi = self.uiSelectBuffer[0] if len(self.uiSelectBuffer) > 0 else self.selectedUi
        self.uiSelectBuffer = []
        self.uiEvents = []

    def updateWindow(self):
        self.dim = pygame.display.get_window_size()

    def update(self):
        self.eventHandler()
        if self.currentScene != None:
            self.currentScene.update(self.delta)
        self.uiLayer.update(self.delta)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT|GL.GL_DEPTH_BUFFER_BIT)
        # self.testDraw()
        self.uiLayer.render()
        return
    
    def testDraw(self):
        vertices = np.array([
            [-0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 0, 0, -1],
            [0.5, -0.5, 0.5, 1.0, 0.0, 1.0, 0, 0, -1],
            [0.5, 0.5, 1.0, 0.0, 1.0, 1.0, 0, 0, -1],
            [-0.5, 0.5, 0.5, 0.0, 1.0, 1.0, 0, 0, -1]
        ], dtype='float32')

        indices = np.array([
            0, 1, 2,
            2, 3, 0
        ], dtype='int32')

        GL.glUseProgram(Assets.GUI_SHADER)

        vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(vao)

        vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices, GL.GL_STATIC_DRAW)

        ebo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, indices, GL.GL_STATIC_DRAW)


        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 9*4, ctypes.c_void_p(0*4))
        GL.glVertexAttribPointer(1, 4, GL.GL_FLOAT, GL.GL_FALSE, 9*4, ctypes.c_void_p(2*4))
        GL.glVertexAttribPointer(2, 2, GL.GL_FLOAT, GL.GL_FALSE, 9*4, ctypes.c_void_p(6*4))
        GL.glVertexAttribPointer(3, 1, GL.GL_FLOAT, GL.GL_FALSE, 9*4, ctypes.c_void_p(8*4))

        GL.glEnableVertexAttribArray(0)
        GL.glEnableVertexAttribArray(1)
        GL.glEnableVertexAttribArray(2)
        GL.glEnableVertexAttribArray(3)
        GL.glDrawElements(GL.GL_TRIANGLES, len(indices), GL.GL_UNSIGNED_INT, None)
        GL.glDisableVertexAttribArray(3)
        GL.glDisableVertexAttribArray(2)
        GL.glDisableVertexAttribArray(1)
        GL.glDisableVertexAttribArray(0)

    def run(self):
        # self.currentScene = self.scenes[2]
        # self.windowWrapper.addChild(self.currentScene.sceneWrapper)
        # self.currentScene.start()

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

    def getWindowScale(self):
        return (self.dim[0]/self.ogdim[0],self.dim[1]/self.ogdim[1])
