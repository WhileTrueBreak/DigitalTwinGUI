from ui.elements.uiButton import UiButton
from ui.elements.uiWrapper import UiWrapper
from ui.elements.ui3dScene import Ui3DScene
from ui.elements.uiStream import UiStream
from ui.elements.uiWrapper import UiWrapper
from ui.elements.uiText import UiText
from ui.elements.uiSlider import UiSlider
from ui.uiHelper import *

from scenes.models.kukaRobot import *
from scenes.ui.pages import Pages

from utils.mathHelper import *
# from utils.kukaIK import *

from connections.opcua import *
from connections.mjpegStream import MJPEGStream

from ui.constraintManager import *
from scenes.scene import *

from asyncua import ua
import pygame
from math import *

class KukaScene(Scene):
    
    def __init__(self, window, name):
        super().__init__(window, name)
        self.cameraTransform = [-0.7+5, -0.57+2, 1.5, -70.25, 0, 45]
        self.camSpeed = 2
        return

    def createUi(self):
        padding = 10
        constraints = [
            ABSOLUTE(T_X, padding),
            ABSOLUTE(T_Y, padding),
            COMPOUND(RELATIVE(T_W, 1, P_W), ABSOLUTE(T_W, -2*padding)),
            COMPOUND(RELATIVE(T_H, 1, P_H), ABSOLUTE(T_H, -2*padding)),
        ]
        self.renderWindow = Ui3DScene(self.window, constraints)
        self.renderWindow.setBackgroundColor((0.2, 0.2, 0.2))
        self.modelRenderer = self.renderWindow.getRenderer()
        self.sceneWrapper.addChild(self.renderWindow)

        padding = 10
        constraints = [
            COMPOUND(COMPOUND(RELATIVE(T_X, 1, P_W), RELATIVE(T_X, -1, T_W)), ABSOLUTE(T_X, -padding)),
            ABSOLUTE(T_Y, padding),
            ABSOLUTE(T_W, 30),
            RELATIVE(T_H, 1, T_W)
        ]
        self.recenterBtn, self.recenterText = centeredTextButton(self.window, constraints)
        self.recenterText.setText('RE')
        self.recenterText.setFontSize(20)
        self.recenterText.setTextSpacing(7)
        self.recenterText.setTextColor((1, 1, 1))
        self.recenterBtn.setDefaultColor((0, 0, 0))
        self.recenterBtn.setHoverColor((0.1, 0.1, 0.1))
        self.recenterBtn.setPressColor((1, 0, 0))
        self.renderWindow.addChild(self.recenterBtn)
        constraints = [
            COMPOUND(RELATIVE(T_X, 0.7, P_W), ABSOLUTE(T_X, padding)),
            ABSOLUTE(T_Y, padding),
            COMPOUND(RELATIVE(T_W, 0.3, P_W), ABSOLUTE(T_W, -2*padding)),
            COMPOUND(RELATIVE(T_H, 1, P_H), ABSOLUTE(T_H, -2*padding)),
        ]

        self.panelWrapper = UiWrapper(self.window, constraints)
        self.sceneWrapper.addChild(self.panelWrapper)
        
        # self.__createArmControlUi()
        self.__createStreams()
        self.__createPrinterUi()

        self.__createRoom()
        self.__addPrinters()
        self.__addFurniture()
        self.__addRobot()
        return

    def __createPrinterUi(self):
        self.printerControlPanels = [None]*len(self.printerStreams)
        self.printerStreamSteals = [None]*len(self.printerStreams)
        self.textImgCombiners = [None]*len(self.printerStreams)
        for i in range(len(self.printerControlPanels)):
            self.printerControlPanels[i] = UiWrapper(self.window, Constraints.ALIGN_PERCENTAGE(0, 0, 1, 1))

            constraints = [
                Constraints.ZERO_ZERO[0],
                RELATIVE(T_Y, -1, T_W),
                RELATIVE(T_W, 1, P_W),
                RELATIVE(T_H, 3/4, T_W)
            ]
            printerStream = UiBlock(self.window, constraints)
            printerStream.setTexture(self.printerStreams[i].texture)
            self.printerControlPanels[i].addChild(printerStream)

    def __createStreams(self):
        self.printerStreams = [None]*5
        self.printerStreams[0] = MJPEGStream('http://172.31.1.229:8080/?action=streams')
        self.printerStreams[1] = MJPEGStream('http://172.31.1.228:8080/?action=streams')
        self.printerStreams[2] = MJPEGStream('http://172.31.1.227:8080/?action=streams')
        self.printerStreams[3] = MJPEGStream('http://172.31.1.226:8080/?action=streams')
        self.printerStreams[4] = MJPEGStream('http://172.31.1.225:8080/?action=streams')
        self.armStream = MJPEGStream('http://172.31.1.177:8080/?action=streams')

    def __createRoom(self):
        roomDim = (7, 15.5)
        roomHeight = 2.7
        self.floor = self.modelRenderer.addModel(Assets.UNIT_WALL, createScaleMatrix(roomDim[0], roomDim[1], 1))
        self.walls = [0]*4
        self.walls[0] = self.modelRenderer.addModel(Assets.UNIT_WALL, 
            createTransformationMatrix(0, 0, roomHeight, 0, 90, 0).dot(createScaleMatrix(roomHeight, roomDim[1], 1)))
        self.walls[1] = self.modelRenderer.addModel(Assets.UNIT_WALL, 
            createTransformationMatrix(roomDim[0], 0, 0, 0, -90, 0).dot(createScaleMatrix(roomHeight, roomDim[1], 1)))
        self.walls[2] = self.modelRenderer.addModel(Assets.UNIT_WALL, 
            createTransformationMatrix(0, roomDim[1], 0, 90, 0, 0).dot(createScaleMatrix(roomDim[0], roomHeight, 1)))
        self.walls[3] = self.modelRenderer.addModel(Assets.UNIT_WALL, 
            createTransformationMatrix(0, 0, roomHeight, -90, 0, 0).dot(createScaleMatrix(roomDim[0], roomHeight, 1)))

    def __addFurniture(self):
        self.benches = [0]*5
        self.benches[0] = self.modelRenderer.addModel(Assets.TABLE_RECT, createTransformationMatrix(7-0.4, 0.8+1.05, 0.85, 0, 0, 0))
        self.benches[1] = self.modelRenderer.addModel(Assets.TABLE_RECT, createTransformationMatrix(7-1.05, 0.4, 0.85, 0, 0, 90))
        self.benches[2] = self.modelRenderer.addModel(Assets.TABLE_SQUARE, createTransformationMatrix(7-0.9, 0.8+2.1+0.9, 0.85, 0, 0, 0))
        self.benches[3] = self.modelRenderer.addModel(Assets.KUKA_BASE, createTransformationMatrix(7-0.9-0.7, 0.8+2.1+0.9-1.6, 0.85+0.06625, 0, 0, 0))
        self.benches[3] = self.modelRenderer.addModel(Assets.KUKA_BASE, createTransformationMatrix(7-1, 0.8+2.1+1.8+0.6, 0.85+0.06625, 0, 0, 0))

        x, y, z = 7-0.9-0.7+0.2, 0.8+2.1+0.9-1.6, 0.85+0.06625

        self.tubeIds = [0]*2
        self.tubeIds[0] = self.modelRenderer.addModel(Assets.TUBE_OUTSIDE, createTransformationMatrix(-0.134+x,0.805+y,0.0225+z,0,0,0))
        self.modelRenderer.setColor(self.tubeIds[0], (1, 1, 0, 1))
        self.tubeIds[1] = self.modelRenderer.addModel(Assets.TUBE_INSIDE, createTransformationMatrix(-0.134+x,0.805+y,0.0225+z,0,0,0))
        self.modelRenderer.setColor(self.tubeIds[1], (0.6, 0.6, 0.6, 1))
        
        self.tubeholderIds = [0]*4
        self.tubeholderIds[0] = self.modelRenderer.addModel(Assets.TUBE_HOLDER, createTransformationMatrix(-0.114+x,0.735+y,-0.06625+z,0,0,90))
        self.modelRenderer.setColor(self.tubeholderIds[0], (0.3, 0.3, 0.3, 1))
        self.tubeholderIds[1] = self.modelRenderer.addModel(Assets.TUBE_HOLDER, createTransformationMatrix(-0.004+x,0.735+y,-0.06625+z,0,0,90))
        self.modelRenderer.setColor(self.tubeholderIds[1], (0.3, 0.3, 0.3, 1))
        self.tubeholderIds[2] = self.modelRenderer.addModel(Assets.TUBE_HOLDER, createTransformationMatrix(-0.114+x,0.875+y,-0.06625+z,0,0,-90))
        self.modelRenderer.setColor(self.tubeholderIds[2], (0.3, 0.3, 0.3, 1))
        self.tubeholderIds[3] = self.modelRenderer.addModel(Assets.TUBE_HOLDER, createTransformationMatrix(-0.004+x,0.875+y,-0.06625+z,0,0,-90))
        self.modelRenderer.setColor(self.tubeholderIds[3], (0.3, 0.3, 0.3, 1))

        self.screenId = self.modelRenderer.addModel(Assets.SCREEN, createTransformationMatrix(6.99, 0.8+2.1+0.9-1, 0.9, 0, -90, 0))
        self.modelRenderer.setTexture(self.screenId, self.armStream.texture)
        self.modelRenderer.setColor(self.screenId, (1,1,1,1))

        self.shelves = [0]*3
        self.shelves[0] = self.modelRenderer.addModel(Assets.SHELF, createTransformationMatrix(7-2.5, 0.8+2.1+1.8+1.3, 0, 0, 0, 0))
        self.shelves[1] = self.modelRenderer.addModel(Assets.SHELF, createTransformationMatrix(7-2.1-2.5,0,0,0,0,0))
        self.shelves[2] = self.modelRenderer.addModel(Assets.SHELF, createTransformationMatrix(1.2,3.9,0,0,0,90))

    def __addRobot(self):
        pos = (7-0.9-0.7+0.2, 0.8+2.1+0.9-1.6, 0.85+0.06625)
        self.kukaTwin = KukaRobotTwin(self.window, pos, 24, 'R4', self.modelRenderer, hasGripper=True, hasForceVector=True)
        self.kukaTwin.setLiveColors([(0.5, i/8, 1.0, 0.7)for i in range(9)])
        self.kukaTwin.setTwinColors([(1.0, 0.5, i/8, 0.0)for i in range(9)])
        self.armControlPanel = self.kukaTwin.getControlPanel()

    def __addPrinters(self):
        printerLoc = [
            [7-0.4, 0.3, 0.85],
            [7-0.4, 1.1, 0.85],
            [7-0.4, 1.6, 0.85],
            [7-0.4, 2.1, 0.85],
            [7-0.4, 2.7, 0.85],
        ]
        
        self.printers = [0]*5
        self.printers[0] = self.modelRenderer.addModel(Assets.ENDER3_3D_PRINTER, createTransformationMatrix(*printerLoc[0], 0, 0, 0))
        self.modelRenderer.setColor(self.printers[0], (0,1,0.0,1))
        self.printers[1] = self.modelRenderer.addModel(Assets.ENDER3_3D_PRINTER, createTransformationMatrix(*printerLoc[1], 0, 0, 0))
        self.modelRenderer.setColor(self.printers[1], (0,1,0.2,1))
        self.printers[2] = self.modelRenderer.addModel(Assets.ENDER3_3D_PRINTER, createTransformationMatrix(*printerLoc[2], 0, 0, 0))
        self.modelRenderer.setColor(self.printers[2], (0,1,0.4,1))
        self.printers[3] = self.modelRenderer.addModel(Assets.ENDER3_3D_PRINTER, createTransformationMatrix(*printerLoc[3], 0, 0, 0))
        self.modelRenderer.setColor(self.printers[3], (0,1,0.6,1))
        self.printers[4] = self.modelRenderer.addModel(Assets.ENDER3_3D_PRINTER, createTransformationMatrix(*printerLoc[4], 0, 0, 0))
        self.modelRenderer.setColor(self.printers[4], (0,1,0.8,1))

        self.printerScreen = [0]*5
        self.printerScreen[0] = self.modelRenderer.addModel(Assets.SCREEN, 
            createTransformationMatrix(printerLoc[0][0]+0.2, printerLoc[0][1]-0.15, printerLoc[0][2]+0.47, 0, -90, 0).dot(createScaleMatrix(0.15, 0.15, 0.15)))
        self.printerScreen[1] = self.modelRenderer.addModel(Assets.SCREEN, 
            createTransformationMatrix(printerLoc[1][0]+0.2, printerLoc[1][1]-0.15, printerLoc[1][2]+0.47, 0, -90, 0).dot(createScaleMatrix(0.15, 0.15, 0.15)))
        self.printerScreen[2] = self.modelRenderer.addModel(Assets.SCREEN, 
            createTransformationMatrix(printerLoc[1][0]+0.2, printerLoc[2][1]-0.15, printerLoc[2][2]+0.47, 0, -90, 0).dot(createScaleMatrix(0.15, 0.15, 0.15)))
        self.printerScreen[3] = self.modelRenderer.addModel(Assets.SCREEN, 
            createTransformationMatrix(printerLoc[1][0]+0.2, printerLoc[3][1]-0.15, printerLoc[3][2]+0.47, 0, -90, 0).dot(createScaleMatrix(0.15, 0.15, 0.15)))
        self.printerScreen[4] = self.modelRenderer.addModel(Assets.SCREEN, 
            createTransformationMatrix(printerLoc[1][0]+0.2, printerLoc[4][1]-0.15, printerLoc[4][2]+0.47, 0, -90, 0).dot(createScaleMatrix(0.15, 0.15, 0.15)))

        for i in range(len(self.printerScreen)):
            self.modelRenderer.setColor(self.printerScreen[i], (1.5,1.5,1.5,1))
            self.modelRenderer.setTexture(self.printerScreen[i], self.printerStreams[i].texture)

    def handleUiEvents(self, event):
        self.kukaTwin.handleEvents(event)
        if event['action'] == 'release':
            if event['obj'] == self.recenterBtn:
                self.cameraTransform = [-0.7+5, -0.57+2, 1.5, -70.25, 0, 45]
            if event['obj'] == self.renderWindow:
                self.__handleSceneEvents(event)
        return
    
    def __handleSceneEvents(self, event):
        modelId = event['modelId']
        padding = 10
        self.panelWrapper.removeAllChildren()
        if self.kukaTwin.isModel(modelId):
            self.renderWindow.updateWidth(COMPOUND(RELATIVE(T_W, 0.7, P_W), ABSOLUTE(T_W, -2*padding)))
            self.panelWrapper.addChild(self.armControlPanel)
        elif modelId in self.printers:
            index = self.printers.index(modelId)
            self.renderWindow.updateWidth(COMPOUND(RELATIVE(T_W, 0.7, P_W), ABSOLUTE(T_W, -2*padding)))
            self.panelWrapper.addChild(self.printerControlPanels[index])
        else:
            self.renderWindow.updateWidth(COMPOUND(RELATIVE(T_W, 1, P_W), ABSOLUTE(T_W, -2*padding)))

    def update(self, delta):
        self.__moveCamera(delta)
        self.__updateStreams(delta)
        self.kukaTwin.update()
        self.modelRenderer.setViewMatrix(createViewMatrix(*self.cameraTransform))
        return

    def __updateStreams(self, delta):
        for stream in self.printerStreams:
            stream.updateImage(delta)
        self.armStream.updateImage(delta)

    def __moveCamera(self, delta): 
        if self.window.selectedUi != self.renderWindow:
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

    @timing
    def start(self):
        self.armStream.start()
        for stream in self.printerStreams:
            stream.start()
        self.threadStopFlag = False
        self.kukaTwin.start()
        return
    
    @timing
    def stop(self):
        self.armStream.stop()
        for stream in self.printerStreams:
            stream.stop()
        self.kukaTwin.stop()
        return
