from uiElement import *
from constraintManager import *

import pygame

import time

class Window:
    def __init__(self, dim, title):
        self.dim = dim
        self.title = title
        
        self.clock = pygame.time.Clock()
        self.running = False

        self.sceneMap = {}

        self.scenes = [None]
        self.currentScene = None

        pygame.init()
        pygame.display.set_caption(self.title)
        self.screen = pygame.display.set_mode(self.dim)

        self.backgroundColor = (255, 200, 200)
        self.mousePos = (0,0)
        self.mouseButtons = [False] * 5
        self.keyState = {}

        self.uiEvents = []
        self.windowWrapper = UiWrapper(self, [], (0,0,*dim))
        self.tabHeight = 40

    def createUi(self):
        self.tabButtons = []
        numBtn = len(self.scenes)
        padding = 10
        for i in range(numBtn):
            constraints = [
                ABSOLUTE(T_Y, padding),
                COMPOUND(RELATIVE(T_X, 1 / numBtn * i, P_W), ABSOLUTE(T_X, padding)),
                COMPOUND(RELATIVE(T_W, 1 / numBtn, P_W), ABSOLUTE(T_W, -2 * padding)),
                ABSOLUTE(T_H, self.tabHeight - 2 * padding)
            ]
            self.tabButtons.append(UiButton(self, constraints))
            self.tabButtons[-1].setText(self.scenes[i].name if self.scenes[i] else 'None')
            self.sceneMap[self.tabButtons[-1]] = self.scenes[i]
        self.windowWrapper.addChildren(*self.tabButtons)

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
            if event['action'] == 'release' and event['obj'] in self.tabButtons:
                print(self.tabButtons)
                print(event['obj'] in self.tabButtons)
                self.currentScene = self.sceneMap[event['obj']]
            if self.currentScene: self.currentScene.eventHandler(event)
        self.uiEvents = []

    def run(self):
        self.running = True
        while self.running:
            timeDelta = self.clock.tick(60)/1000.0
            self.eventHandler()
            self.windowWrapper.update()
            if(self.currentScene): self.currentScene.update(timeDelta)

            self.screen.fill(self.backgroundColor)

            self.windowWrapper.render()
            if(self.currentScene): self.currentScene.render()
            
            pygame.display.flip()
