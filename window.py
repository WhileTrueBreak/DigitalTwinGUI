import pygame
import pygame_gui

from pygame_gui.ui_manager import UIManager
from pygame_gui.core import IncrementalThreadedResourceLoader, ObjectID

from pygame_gui.elements import *

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

        self.loader = IncrementalThreadedResourceLoader()
        self.uiManager = UIManager(self.dim, '', resource_loader=self.loader)

        self.backgroundSurface = pygame.Surface(self.dim)
        self.backgroundSurface.fill(pygame.Color("#000000"))

    def createUi(self):
        self.tabButtons = []
        numBtn = len(self.scenes)
        for i in range(numBtn):
            btn = UIButton(pygame.Rect((int(self.dim[0] / numBtn * i), 0),(int(self.dim[0] / numBtn), int(self.dim[1] * 0.05))),
                           self.scenes[i].name if self.scenes[i] else 'None',
                           self.uiManager)
            self.sceneMap[btn] = self.scenes[i]
            self.tabButtons.append(btn)

    def eventHandler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element in self.sceneMap:
                    self.currentScene = self.sceneMap[event.ui_element]
            if(self.currentScene): self.currentScene.eventHandler(event)
            self.uiManager.process_events(event)

    def run(self):
        self.running = True
        while self.running:
            timeDelta = self.clock.tick(60)/1000.0
            self.eventHandler()
            
            if(self.currentScene): self.currentScene.update(timeDelta)
            self.uiManager.update(timeDelta)
            
            self.screen.blit(self.backgroundSurface, (0, 0))

            if(self.currentScene): self.currentScene.render()
            self.uiManager.draw_ui(self.screen)

            pygame.display.update()
    
    def setBGColor(self, hex):
        self.backgroundSurface.fill(pygame.Color(hex))

print('imported window')