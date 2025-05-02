from asset import *

from connections.mjpegStream import MJPEGStream

from scenes.scene import Scene
from scenes.utils.movingCamera import MovingCamera
from scenes.utils.sceneLoader import SceneLoader
from scenes.utils.wallBuilder import WallBuilder

from models.interfaces.model import SimpleModel, Updatable, Serializable
from models.interfaces.interactable import Interactable
from models.staticModel import StaticModel
from models.wrapper.keyPoints.zedHeadKeypoints import ZedHeadKeypoints
from models.wrapper.kuka.kukaBase import KukaBase
from models.wrapper.kuka.kukaRobot import KukaRobotTwin

from ui.elements.uiButton import UiButton
from ui.elements.uiWrapper import UiWrapper
from ui.elements.ui3dScene import Ui3DScene
from ui.elements.uiStream import UiStream
from ui.elements.uiWrapper import UiWrapper
from ui.elements.uiText import UiText
from ui.elements.uiSlider import UiSlider
from ui.constraintManager import *
from ui.uiHelper import *

from utils.interfaces.pollController import PollController
from utils.mathHelper import *
from utils.objMesh import *
from utils.videoPlayer import *

import numpy as np
import pickle
import shutil
import time
import os

class ExpoScene(Scene):

    UI_PADDING = 10

    def __init__(self, window, name):
        super().__init__(window, name)
        self.models = []
        
        self.camera = MovingCamera(self.window, [3, -2, 2, -90, 0, 0], 2)
        
        self.pointLight = (-1, 3, 1.5)
        self.lapsed = 0
    
    @timing
    def createUi(self):
        self.renderWindow = Ui3DScene(self.window, Constraints.ALIGN_PERCENTAGE_PADDING(0, 0, 1, 1, ExpoScene.UI_PADDING), supportTransparency=True)
        self.renderWindow.setBackgroundColor((0.25, 0.2, 0.27))
        self.modelRenderer = self.renderWindow.getRenderer()
        self.sceneWrapper.addChild(self.renderWindow)
        
        self.panelWrapper = UiWrapper(self.window, Constraints.ALIGN_PERCENTAGE_PADDING(0.7,0,0.3,1, ExpoScene.UI_PADDING))
        self.renderWindow.addChild(self.panelWrapper)

        self.__createRoom()
        self.__fillRoom()
        return
    
    @timing
    def __createRoom(self):
        w = 6
        d = 2.5
        h = 2.481
        banner_h = 0.5
        bar_w = 0.01

        planes = []
        planes.append(WallBuilder.buildPlaneXY(0, 0, 0, 6, 2.5))
        planes.append(WallBuilder.buildPlaneXY(w/2-bar_w/2,0,h-bar_w,bar_w,h))
        planes.append(WallBuilder.buildPlaneXY(w/2-bar_w/2,0,h,bar_w,h))
        planes.append(WallBuilder.buildPlaneYZ(w/2-bar_w/2,0,h-bar_w,h,bar_w))
        planes.append(WallBuilder.buildPlaneYZ(w/2+bar_w/2,0,h-bar_w,h,bar_w))
        planes.append(WallBuilder.buildPlaneXZ(w/2-bar_w/2,0,0,bar_w,h))
        planes.append(WallBuilder.buildPlaneXZ(w/2+bar_w/2,0,0,bar_w,h))
        planes.append(WallBuilder.buildPlaneYZ(w/2-bar_w/2,0,0,bar_w,h))
        planes.append(WallBuilder.buildPlaneYZ(w/2+bar_w/2,0,0,bar_w,h))

         #New Lab
        wallplan = [
            # ((0,0),(0,d),(0,h)),#LEFT WALL
            ((0,d),(w,d),(0,h)),#BACK WALL     
            # ((w,0),(w,d),(0,h)),#RIGHT WALL 
            ((0,-0.001),(w,-0.001),(h-banner_h,h)),#FRONT PANEL
        ]

        roomColor = (0.9,0.9,0.9,1)

        planes.extend(WallBuilder.buildWallPlan(wallplan))
        roomPlan = ObjMesh.fromSubModels(planes)[0]
        roomModel = SimpleModel(self.modelRenderer, roomPlan, np.identity(4))
        self.models.append(roomModel)
        self.modelRenderer.setColor(roomModel.modelId, roomColor)
        return

    @timing
    def __fillRoom(self):
        # trolley
        trolleyModel = StaticModel(self.modelRenderer, Assets.EXPO_TROLLEY, createTransformationMatrix(2,0.6,0.124,0,0,-90))

        # zed camera
        ZED_Camera = StaticModel(self.modelRenderer, Assets.ZED_CAMERA, createTransformationMatrix(0.3201, 0, 0.643, 0, 0, 90))
        ZED_Keypoints = ZedHeadKeypoints(self.modelRenderer)
        ZED_Camera.setAttach(trolleyModel)
        ZED_Keypoints.setAttach(ZED_Camera)

        # kuka robot
        kukaRobot = KukaRobotTwin(self.window, createTransformationMatrix(0, 0, 0.643, 0, 0, 0), 23, 'R3', self.modelRenderer, hasForceVector=True, hasGripper=True)
        kukaRobot.setLiveColors([(1, 51/255, 51/255, 0.7)for i in range(9)])
        kukaRobot.setTwinColors([(1, 178/255, 102/255, 0.0)for i in range(9)])
        kukaRobot.setAttach(trolleyModel)

        # furniture
        barstool1 = SimpleModel(self.modelRenderer, Assets.BAR_STOOL, createTransformationMatrix(1.5, 2, 0, 0, 0, 0))
        self.modelRenderer.setColor(barstool1.modelId, (121/255,85/255,73/255,1))
        barstool2 = SimpleModel(self.modelRenderer, Assets.BAR_STOOL, createTransformationMatrix(2.5, 2, 0, 0, 0, 0))
        self.modelRenderer.setColor(barstool2.modelId, (121/255,85/255,73/255,1))
        counter = SimpleModel(self.modelRenderer, Assets.COUNTER, createTransformationMatrix(4, 0.5, 0, 0, 0, 0))
        self.modelRenderer.setColor(counter.modelId, (0,109/255,174/255,1))
        self.models.append(barstool1)
        self.models.append(barstool2)
        self.models.append(counter)

        self.models.append(trolleyModel)
        self.models.append(ZED_Camera)
        self.models.append(ZED_Keypoints)
        self.models.append(kukaRobot)

    def handleUiEvents(self, event):
        for model in self.models:
            if not isinstance(model, Interactable): continue
            model.handleEvents(event)
        if event['action'] == 'release':
            if event['obj'] == self.renderWindow:
                self.__handleSceneEvents(event)
        return
    
    def __handleSceneEvents(self, event):
        modelId = event['modelId']
        self.panelWrapper.removeAllChildren()
        for model in self.models:
            if model.isModel(modelId):
                if not isinstance(model, Interactable): continue
                cp = model.getControlPanel()
                if not cp: break
                self.panelWrapper.addChild(cp)

    @funcProfiler(ftype='sceneupdate')
    def update(self, delta):
        self.__updateEnv(delta)
        self.__updateModelPos()
        self.__updateView()
        self.__updateLight(delta)

        for model in self.models:
            if not isinstance(model, Updatable): continue
            model.update(delta)
    
    def __updateLight(self, delta):
        self.pointLight = (-1 + 1.5*cos(self.lapsed/4), 3 + 1.5*sin(self.lapsed/4), 2)
        self.lapsed += delta
        self.modelRenderer.setLight(self.pointLight)

    def __updateView(self):
        for model in self.models:
            if not hasattr(model, 'inViewFrustrum'): continue
            if not hasattr(model, 'setViewFlag'): continue
            inView = model.inViewFrustrum(self.modelRenderer.projectionMatrix, self.modelRenderer.viewMatrix)

    def __updateModelPos(self):
        return
    
    def __updateEnv(self, delta):
        if self.window.selectedUi == self.renderWindow:
            self.camera.moveCamera(delta)
        if self.camera.hasMoved():
            self.modelRenderer.setViewMatrix(createViewMatrix(*self.camera.getCameraTransform()))

    @timing
    def start(self):
        self.modelRenderer.setViewMatrix(createViewMatrix(*self.camera.getCameraTransform()))
        [model.start() for model in self.models if isinstance(model, PollController)]
        return

    @timing
    def stop(self):
        self.save('save')

        [model.stop() for model in self.models if isinstance(model, PollController)]
        return

    @timing
    def save(self, loc):
        if os.path.exists(loc):
            shutil.rmtree(loc)
        for model in self.models:
            if not isinstance(model, Serializable): continue
            model.serialize(loc)



