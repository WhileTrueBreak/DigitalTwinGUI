from ui.elements.ui3dScene import Ui3DScene

from ui.constraintManager import *
from ui.uiHelper import *

from utils.mathHelper import *

from scenes.scene import *

import numpy as np
import random

class LimitScene(Scene):

    def __init__(self, window, name):
        super().__init__(window, name)
        self.cameraTransform = [1.5, -1.2, 0.8, -425, 0, -406.27]
        self.camSpeed = 2
    
    def createUi(self):
        self.renderArea = Ui3DScene(self.window, Constraints.ALIGN_PERCENTAGE(0, 0, 1, 1))
        self.renderArea.setBackgroundColor((1, 1, 1))
        self.modelRenderer = self.renderArea.getRenderer()
        self.sceneWrapper.addChild(self.renderArea)

        self.__createModels()
        return
    
    def __createModels(self):
        size = 100
        for i in range(size): 
            for j in range(size):
                for k in range(size):
                    if random.random() < 0.3:
                        continue;
                    cube = self.modelRenderer.addModel(self.__createCube(i,j,k), createTransformationMatrix(0,0,0,0,0,0))
                    self.modelRenderer.setColor(cube, (random.random(),random.random(),random.random(),1))
        return

    def __createCube(self, x, y, z):
        half_side = 0.5
        vertices = np.array([
            # Front face
            [-half_side + x, -half_side + y, half_side + z],   # Bottom-left
            [half_side + x, -half_side + y, half_side + z],    # Bottom-right
            [half_side + x, half_side + y, half_side + z],     # Top-right
            [-half_side + x, half_side + y, half_side + z],    # Top-left

            # Back face
            [-half_side + x, -half_side + y, -half_side + z],  # Bottom-left
            [half_side + x, -half_side + y, -half_side + z],   # Bottom-right
            [half_side + x, half_side + y, -half_side + z],    # Top-right
            [-half_side + x, half_side + y, -half_side + z],   # Top-left

            # Left face
            [-half_side + x, -half_side + y, -half_side + z],  # Bottom-back
            [-half_side + x, -half_side + y, half_side + z],   # Bottom-front
            [-half_side + x, half_side + y, half_side + z],    # Top-front
            [-half_side + x, half_side + y, -half_side + z],   # Top-back

            # Right face
            [half_side + x, -half_side + y, -half_side + z],   # Bottom-back
            [half_side + x, -half_side + y, half_side + z],    # Bottom-front
            [half_side + x, half_side + y, half_side + z],     # Top-front
            [half_side + x, half_side + y, -half_side + z],    # Top-back

            # Top face
            [-half_side + x, half_side + y, half_side + z],    # Front-left
            [half_side + x, half_side + y, half_side + z],     # Front-right
            [half_side + x, half_side + y, -half_side + z],    # Back-right
            [-half_side + x, half_side + y, -half_side + z],   # Back-left

            # Bottom face
            [-half_side + x, -half_side + y, half_side + z],   # Front-left
            [half_side + x, -half_side + y, half_side + z],    # Front-right
            [half_side + x, -half_side + y, -half_side + z],   # Back-right
            [-half_side + x, -half_side + y, -half_side + z],  # Back-left
        ], dtype=np.float32)
        indices = np.array([
            # Front face
            0, 1, 2,
            2, 3, 0,

            # Back face
            4, 6, 5,
            6, 4, 7,

            # Left face
            8, 9, 10,
            10, 11, 8,

            # Right face
            12, 14, 13,
            14, 12, 15,

            # Top face
            16, 17, 18,
            18, 19, 16,

            # Bottom face
            20, 22, 21,
            22, 20, 23
        ], dtype=np.uint32)
        return Model.fromVertIndex(vertices, indices)[0]

    def handleUiEvents(self, event):
        return

    def absUpdate(self, delta):
        self.__moveCamera(delta)
        self.modelRenderer.setViewMatrix(createViewMatrix(*self.cameraTransform))
        return

    def start(self):
        return

    def stop(self):
        return

    def __moveCamera(self, delta):
        if self.window.selectedUi != self.renderArea:
            return

        if self.window.getKeyState(pygame.K_j):
            self.cameraTransform[5] -= 90*delta
        if self.window.getKeyState(pygame.K_l):
            self.cameraTransform[5] += 90*delta
        if self.window.getKeyState(pygame.K_i):
            self.cameraTransform[3] += 90*delta
        if self.window.getKeyState(pygame.K_k):
            self.cameraTransform[3] -= 90*delta
        
        deltaPos = [0,0,0]
        if self.window.getKeyState(pygame.K_a): #left
            deltaPos[0] -= 1
        if self.window.getKeyState(pygame.K_d): #right
            deltaPos[0] += 1
        if self.window.getKeyState(pygame.K_w): #forward
            deltaPos[1] -= 1
        if self.window.getKeyState(pygame.K_s): #back
            deltaPos[1] += 1
        if self.window.getKeyState(pygame.K_LALT): #down
            deltaPos[2] -= 1
        if self.window.getKeyState(pygame.K_SPACE): #up
            deltaPos[2] += 1
        deltaPos = [x*delta*self.camSpeed for x in normalize(deltaPos)]
        radPitch = radians(self.cameraTransform[3])
        radYaw = radians(self.cameraTransform[5])

        yawX =  deltaPos[0]*cos(radYaw)#+deltaPos[2]*sin(radYaw)
        yawY =  -deltaPos[0]*sin(radYaw)#+deltaPos[2]*cos(radYaw)

        self.cameraTransform[0] += yawX-deltaPos[1]*sin(radYaw)#*sin(radPitch)
        self.cameraTransform[1] += yawY-deltaPos[1]*cos(radYaw)#*sin(radPitch)
        self.cameraTransform[2] += -deltaPos[2]*sin(radPitch)#+deltaPos[1]*cos(radPitch)

