from asset import *

from scenes.scene import Scene
from scenes.models.GenericModel import GenericModel
from scenes.models.kukaRobot import KukaRobotTwin
from scenes.utils.MovingCamera import MovingCamera
from scenes.utils.Builder import Builder

from ui.elements.uiButton import UiButton
from ui.elements.uiWrapper import UiWrapper
from ui.elements.ui3dScene import Ui3DScene
from ui.elements.uiStream import UiStream
from ui.elements.uiWrapper import UiWrapper
from ui.elements.uiText import UiText
from ui.elements.uiSlider import UiSlider
from ui.constraintManager import *
from ui.uiHelper import *

from utils.mathHelper import *

import numpy as np
import time

class DigitalTwinLab(Scene):

    UI_PADDING = 10

    def __init__(self, window, name):
        super().__init__(window, name)
        self.camera = MovingCamera(self.window, [12, 3, 1.5, -90, 0, -50], 1)

    @timing
    def createUi(self):
        self.renderWindow = Ui3DScene(self.window, Constraints.ALIGN_PERCENTAGE_PADDING(0, 0, 1, 1, DigitalTwinLab.UI_PADDING))
        self.renderWindow.setBackgroundColor((0.2, 0.2, 0.2))
        self.modelRenderer = self.renderWindow.getRenderer()
        self.sceneWrapper.addChild(self.renderWindow)
        
        self.panelWrapper = UiWrapper(self.window, Constraints.ALIGN_PERCENTAGE_PADDING(0.7,0,0.3,1, DigitalTwinLab.UI_PADDING))
        self.sceneWrapper.addChild(self.panelWrapper)

        self.__createRoom()
        self.__addRobots()
        self.__addFurniture()
        return
    
    def __createRoom(self):
        plan = [
            #right
            [(0,0),(0,1.1),(0,2.4)],
            [(0,1.1),(0,1.26),(0,3.1)],
            [(0,1.26),(0,6.92),(0,0.885)],
            [(0,6.92),(0,7),(0,3.1)],
            [(0,1.1),(0,6.92),(2.4,3.1)],

            #front
            [(0,0),(0.47,0),(0,2.4)],
            [(0.47,0),(1.47,0),(0,0.885)],
            [(3.77,0),(5.77,0),(0,0.885)],
            [(5.77,0),(6.39,0),(0,2.4)],
            [(6.39,0),(8.39,0),(0,0.885)],
            [(10.69,0),(11.69,0),(0,0.885)],
            [(11.69,0),(12.34,0),(0,2.4)],
            [(12.34,0),(15.3,0),(0,0.885)],

            #left door
            [(15.3,0),(15.3,1),(0,2.4)],
            [(15.3,1),(15.3,2.75),(0,0.885)],
            [(15.3,2.75),(15.3,2.9),(0,3.1)],
            [(15.3,5),(15.3,7),(0,3.1)],
            [(15.3,1.1),(15.3,7),(2.4,3.1)],

            [(15.43, 2.9), (15.3, 2.9), (0, 2.4)],
            [(15.43, 5), (15.3, 5), (0, 2.4)],

            [(15.43, 1), (15.3, 1), (0.885, 2.4)],
            [(15.43, 2.75), (15.3, 2.75), (0.885, 2.4)],

            #back
            [(0,7),(15.3,7),(0,0.885)],

            [(14.1,7),(15.3,7),(0.885,2.4)],
            [(12.32,7),(13.26,7),(0.885,2.4)],

            [(0,7),(1.3,7),(0.885,2.4)],
            [(2.15,7),(4,7),(0.885,2.4)],
            [(4.84,7),(5.94,7),(0.885,2.4)],

            [(6.31,7),(7.31,7),(0.885,2.4)],
            [(8.16,7),(9.9,7),(0.885,2.4)],
            [(10.75,7),(11.95,7),(0.885,2.4)],

            [(0,7),(15.3,7),(2.4,3.1)],
            
            #back pillars
            [(0,6.92),(0.3,6.92),(0,3.1)],
            [(0.3,6.92),(0.3,7),(0,3.1)],
            [(5.94,6.92),(6.31,6.92),(0,3.1)],
            [(5.94,6.92),(5.94,7),(0,3.1)],
            [(6.31,6.92),(6.31,7),(0,3.1)],
            [(11.95,6.92),(12.32,6.92),(0,3.1)],
            [(11.95,6.92),(11.95,7),(0,3.1)],
            [(12.32,6.92),(12.32,7),(0,3.1)],

            #side room
            [(15.3, 1),(17.96, 1),(0, 2.4)],
            [(17.96, 1),(17.96, 7),(0, 2.4)],
            [(15.43, 5),(15.43, 7),(0, 2.4)],
            [(15.3, 7),(17.96, 7),(0, 2.4)],
            [(15.43,1),(15.43,2.75),(0,0.885)],
            [(15.43,2.75),(15.43,2.9),(0,2.4)]]
        for plane in Builder.buildWallPlan(plan):
            mid = self.modelRenderer.addModel(plane, np.identity(4))
            self.modelRenderer.setColor(mid, (1,1,1,1))
        
        xyPlanes = [
            (0, 0, 2.4, 15.3, 1.1, Builder.S2),
            (0, 0, 0, 15.3, 7, Builder.S1|Builder.S2),
            (0, 1.1, 3.1, 15.3, 5.9, Builder.S2),
            (15.3, 1, 0, 0.13, 6, Builder.S1|Builder.S2),
            (15.3, 1, 0.885, 0.13, 1.75, Builder.S1),
            (15.3, 1, 2.4, 0.13, 6, Builder.S1|Builder.S2),
            (15.43, 1, 0, 2.53, 6, Builder.S1|Builder.S2),
            (15.43, 1, 2.4, 2.53, 6, Builder.S2)]
        for plane in xyPlanes:
            mid = self.modelRenderer.addModel(Builder.buildPlaneXY(*plane[0:5], vis=plane[5]), np.identity(4))
            self.modelRenderer.setColor(mid, (1,1,1,1))

        mid = self.modelRenderer.addModel(Builder.buildPlaneXZ(0, 1.1, 2.4, 15.3, 0.7, vis=Builder.S2), np.identity(4))
        self.modelRenderer.setColor(mid, (1,1,1,1))
        return

    def __addRobots(self):
        self.genericModels = []
        self.arms = {}

        base = GenericModel(self.window, self.modelRenderer, Assets.KUKA_FLEX, createTransformationMatrix(5, 4.9, 0.89, 0, 0, 180))
        arm = KukaRobotTwin(self.window, createTransformationMatrix(0.315, 0, 0, 0, 0, 0), 21, 'R1', self.modelRenderer, hasForceVector=True, hasGripper=True)
        arm.setLiveColors([(0.5, i/8, 1.0, 0.7)for i in range(9)])
        arm.setTwinColors([(1.0, 0.5, i/8, 0.0)for i in range(9)])
        self.genericModels.append(base)
        self.arms[base] = arm

        base = GenericModel(self.window, self.modelRenderer, Assets.KUKA_FLEX, createTransformationMatrix(8.5, 0.75, 0.89, 0, 0, 90))
        arm = KukaRobotTwin(self.window, createTransformationMatrix(0.315, 0, 0, 0, 0, 0), 22, 'R2', self.modelRenderer, hasForceVector=True, hasGripper=True)
        arm.setLiveColors([(0.5, i/8, 1.0, 0.7)for i in range(9)])
        arm.setTwinColors([(1.0, 0.5, i/8, 0.0)for i in range(9)])
        self.genericModels.append(base)
        self.arms[base] = arm
        
        base = GenericModel(self.window, self.modelRenderer, Assets.OMNIMOVE, createTransformationMatrix(13, 3, 0.7, 0, 0, 180))
        arm = KukaRobotTwin(self.window, createTransformationMatrix(0.363, -0.184, 0, 0, 0, -90), 23, 'R3', self.modelRenderer, hasForceVector=True, hasGripper=True)
        arm.setLiveColors([(0.5, i/8, 1.0, 0.7)for i in range(9)])
        arm.setTwinColors([(1.0, 0.5, i/8, 0.0)for i in range(9)])
        self.genericModels.append(base)
        self.arms[base] = arm
        
        base = GenericModel(self.window, self.modelRenderer, Assets.OMNIMOVE, createTransformationMatrix(11, 3, 0.7, 0, 0, 0))
        arm = KukaRobotTwin(self.window, createTransformationMatrix(0.363, -0.184, 0, 0, 0, -90), 24, 'R4', self.modelRenderer, hasForceVector=True, hasGripper=True)
        arm.setLiveColors([(0.5, i/8, 1.0, 0.7)for i in range(9)])
        arm.setTwinColors([(1.0, 0.5, i/8, 0.0)for i in range(9)])
        self.genericModels.append(base)
        self.arms[base] = arm

        # [self.modelRenderer.setColor(model.modelId, (1,1,1,0.5)) for model in self.genericModels]

    def __addFurniture(self): 
        self.shelves = []
        self.shelves.append(self.modelRenderer.addModel(Assets.SHELF, createTransformationMatrix(14.70,7,0,0,0,-90)))
        self.shelves.append(self.modelRenderer.addModel(Assets.SHELF, createTransformationMatrix(12.66,7,0,0,0,-90)))
        self.shelves.append(self.modelRenderer.addModel(Assets.SHELF, createTransformationMatrix(11.35,7,0,0,0,-90)))
        self.shelves.append(self.modelRenderer.addModel(Assets.SHELF, createTransformationMatrix(10.75,7,0,0,0,-90)))

        self.tables = []
        self.tables.append(self.modelRenderer.addModel(Assets.TABLES[1], createTransformationMatrix(2.5,7-1.05,0.85,0,0,0)))
        self.tables.append(self.modelRenderer.addModel(Assets.TABLES[2], createTransformationMatrix(4.8,7-0.9,0.85,0,0,0)))
        self.tables.append(self.modelRenderer.addModel(Assets.TABLES[1], createTransformationMatrix(6.8,7-1.05,0.85,0,0,0)))

    def handleUiEvents(self, event):
        [arm.handleEvents(event) for arm in self.arms.values()]
        [model.handleEvents(event) for model in self.genericModels]
        if event['action'] == 'release':
            if event['obj'] == self.renderWindow:
                self.__handleSceneEvents(event)
        return
    
    def __handleSceneEvents(self, event):
        modelId = event['modelId']
        self.panelWrapper.removeAllChildren()
        for arm in self.arms.values():
            if arm.isModel(modelId):
                self.renderWindow.updateWidth(COMPOUND(RELATIVE(T_W, 0.7, P_W), ABSOLUTE(T_W, -2*DigitalTwinLab.UI_PADDING)))
                self.panelWrapper.addChild(arm.getControlPanel())
        for model in self.genericModels:
            if model.isModel(modelId):
                self.renderWindow.updateWidth(COMPOUND(RELATIVE(T_W, 0.7, P_W), ABSOLUTE(T_W, -2*DigitalTwinLab.UI_PADDING)))
                self.panelWrapper.addChild(model.getControlPanel())
        if len(self.panelWrapper.children) == 0:
            self.renderWindow.updateWidth(COMPOUND(RELATIVE(T_W, 1, P_W), ABSOLUTE(T_W, -2*DigitalTwinLab.UI_PADDING)))
    
    def update(self, delta):
        self.__updateEnv(delta)
        self.__updateModelPos()
        [arm.update() for arm in self.arms.values()]
        [model.update() for model in self.genericModels]
        return
    
    def __updateModelPos(self):
        for base in self.arms:
            self.arms[base].setAttach(base.getFrame())
        return
    
    def __updateEnv(self, delta):
        if self.window.selectedUi == self.renderWindow:
            self.camera.moveCamera(delta)
        if self.camera.hasMoved():
            self.modelRenderer.setViewMatrix(createViewMatrix(*self.camera.getCameraTransform()))
        
    def start(self):
        [arm.start() for arm in self.arms.values()]
        return
        
    def stop(self):
        [arm.stop() for arm in self.arms.values()]
        return





