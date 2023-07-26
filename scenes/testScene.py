from asset import *

from connections.mjpegStream import MJPEGStream

from scenes.scene import Scene
from scenes.models.genericModel import GenericModel
from scenes.models.kukaRobot import KukaRobotTwin
from scenes.utils.movingCamera import MovingCamera
from scenes.utils.builder import Builder

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

class TestScene(Scene):

    UI_PADDING = 10

    def __init__(self, window, name):
        super().__init__(window, name)
        self.camera = MovingCamera(self.window, [0,0,0,0,0,0], 1)
    @timing
    def createUi(self):
        self.renderWindow = Ui3DScene(self.window, Constraints.ALIGN_PERCENTAGE_PADDING(0, 0, 1, 1, TestScene.UI_PADDING))
        self.renderWindow.setBackgroundColor((0.2, 0.2, 0.2))
        self.modelRenderer = self.renderWindow.getRenderer()
        self.sceneWrapper.addChild(self.renderWindow)
        
        self.panelWrapper = UiWrapper(self.window, Constraints.ALIGN_PERCENTAGE_PADDING(0.7,0,0.3,1, TestScene.UI_PADDING))
        self.sceneWrapper.addChild(self.panelWrapper)

        self.screen = self.modelRenderer.addModel(Assets.KUKA_FLEX, createTransformationMatrix(0,0,0,90,0,0))
        self.modelRenderer.setColor(self.screen, (1,0,0,1))

    def handleUiEvents(self, event):
        return
    
    def update(self, delta):
        self.__updateEnv(delta)
        return
    
    def __updateEnv(self, delta):
        if self.window.selectedUi == self.renderWindow:
            self.camera.moveCamera(delta)
        if self.camera.hasMoved():
            self.modelRenderer.setViewMatrix(createViewMatrix(*self.camera.getCameraTransform()))
        
    def start(self):
        return
        
    def stop(self):
        return





