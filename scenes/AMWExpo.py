from ui.elements.uiButton import UiButton
from ui.elements.ui3dScene import Ui3DScene
from ui.elements.uiWrapper import UiWrapper
from ui.elements.uiStream import UiStream
from ui.elements.uiWrapper import UiWrapper
from ui.elements.uiText import UiText
from ui.elements.uiSlider import UiSlider

from connections.mjpegStream import MJPEGStream
from connections.opcua import *

from utils.uiHelper import *
from utils.mathHelper import *

from ui.constraintManager import *
from scenes.scene import *

from asyncua import ua
import pygame
from math import *

def DH(DH_table):
    T_0_ = np.ndarray(shape=(len(DH_table)+1,4,4))
    T_0_[:][:][0] = np.eye(4)
    T_i_ = np.ndarray(shape=(len(DH_table),4,4))
    for i in range(len(DH_table)):
        alp = DH_table[i][0]
        a = DH_table[i][1]
        d = DH_table[i][2]
        the = DH_table[i][3]

        T = np.array([[np.cos(the),-np.sin(the),0,a],
            [np.sin(the)*np.cos(alp),np.cos(the)*np.cos(alp),-np.sin(alp),-np.sin(alp)*d],
            [np.sin(the)*np.sin(alp),np.cos(the)*np.sin(alp),np.cos(alp),np.cos(alp)*d],
            [0,0,0,1]])

        T_0_[:][:][i+1] = np.matmul(T_0_[:][:][i],T)
        T_i_[:][:][i] = T
    return T_0_ ,T_i_

def T_KUKAiiwa14(q):
    DH_Robot1 = np.array([[0, 0, 0.36, q[0]], 
        [-np.pi/2, 0, 0 , q[1]],
        [np.pi/2, 0, 0.42 , q[2]],
        [np.pi/2, 0, 0, q[3]],
        [-np.pi/2, 0, 0.4, q[4]],
        [-np.pi/2, 0, 0, q[5]],
        [np.pi/2, 0, 0.15194, q[6]]])

    Robot1_T_0_ , Robot1_T_i_ = DH(DH_Robot1)
    return Robot1_T_0_ , Robot1_T_i_

class AMWExpo(Scene):
    
    def __init__(self, window, name):
        super().__init__(window, name)
        self.planes = [] #pre allocated walls, can we append??

        self.cameraTransform = [-0.7+5, -0.57+2, 1.5, -70.25, 0, 45]
        self.camSpeed = 2

        self.progid = 2

        self.jointsRad = [0,0,0,0,0,0,0]
        self.twinJoints = [0,0,0,0,0,0,0]
        self.matchLive = True
        self.forceVector = np.array([0,0,0], dtype='float32')

        self.threadStopFlag = True
        self.opcuaReceiverContainer = OpcuaContainer()
        
        self.dataThread = Opcua.createOpcuaReceiverThread(self.opcuaReceiverContainer, 'oct.tpc://172.31.1.236:4840/server/', 
            [
                'ns=24;s=R4d_Joi1', 
                'ns=24;s=R4d_Joi2', 
                'ns=24;s=R4d_Joi3', 
                'ns=24;s=R4d_Joi4', 
                'ns=24;s=R4d_Joi5', 
                'ns=24;s=R4d_Joi6', 
                'ns=24;s=R4d_Joi7'
            ], lambda:self.threadStopFlag)
        self.forceThread = Opcua.createOpcuaReceiverThread(self.opcuaReceiverContainer, 'oct.tpc://172.31.1.236:4840/server/', 
            [
                'ns=24;s=R4d_ForX', 
                'ns=24;s=R4d_ForY', 
                'ns=24;s=R4d_ForZ' 
            ], lambda:self.threadStopFlag)
        self.progControlThread = Opcua.createOpcuaReceiverThread(self.opcuaReceiverContainer, 'oct.tpc://172.31.1.236:4840/server/', 
            [
                'ns=24;s=R4c_ProgID', 
                'ns=24;s=R4c_Start',    
                'ns=24;s=R4f_Ready', 
                'ns=24;s=R4f_End',  
            ], lambda:self.threadStopFlag)

        self.progStartFlag = False
        self.executingFlag = False
        self.doneFlag = False

        self.opcuaTransmitterContainer = OpcuaContainer()
        self.transmitter = Opcua.createOpcuaTransmitterThread(self.opcuaTransmitterContainer, 'oct.tpc://172.31.1.236:4840/server/', lambda:self.threadStopFlag)
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
        self.renderWindow.setBackgroundColor((1, 1, 1))
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
            COMPOUND(RELATIVE(T_H, 0.8, P_H), ABSOLUTE(T_H, -2*padding)),
        ]

        self.panelWrapper = UiWrapper(self.window, constraints)
        self.sceneWrapper.addChild(self.panelWrapper)
        
        self.__createArmControlUi()
        self.__createStreams()

        self.__createRoom()
        self.__addFurniture()
        self.__addRobot()
        return

    def __createArmControlUi(self):
        self.armControlPanel = UiWrapper(self.window, Constraints.ALIGN_PERCENTAGE(0, 0, 1, 1))

        self.selecterWrappers = [None]*7
        padding = 5
        for i in range(len(self.selecterWrappers)):
            constraints = [
                ABSOLUTE(T_X, padding),
                COMPOUND(RELATIVE(T_Y, 0.1*i, P_H), ABSOLUTE(T_Y, padding)),
                COMPOUND(RELATIVE(T_W, 1, P_W), ABSOLUTE(T_W, -2*padding)),
                COMPOUND(RELATIVE(T_H, 0.1, P_H), ABSOLUTE(T_H, -2*padding)),
            ]
            self.selecterWrappers[i] = UiWrapper(self.window, constraints)
        self.armControlPanel.addChildren(*self.selecterWrappers)

        self.liveTextWrapper = [None]*len(self.selecterWrappers)
        self.liveAngleText = [None]*len(self.selecterWrappers)
        self.twinTextWrapper = [None]*len(self.selecterWrappers)
        self.twinAngleText = [None]*len(self.selecterWrappers)

        self.angleSlider = [None]*len(self.selecterWrappers)
        for i in range(len(self.selecterWrappers)):
            self.liveTextWrapper[i] = UiWrapper(self.window, Constraints.ALIGN_PERCENTAGE(0, 0, 0.5, 0.5))
            self.twinTextWrapper[i] = UiWrapper(self.window, Constraints.ALIGN_PERCENTAGE(0.5, 0, 0.5, 0.5))
            self.selecterWrappers[i].addChild(self.liveTextWrapper[i])
            self.selecterWrappers[i].addChild(self.twinTextWrapper[i])
            self.liveAngleText[i] = UiText(self.window, Constraints.ALIGN_TEXT_PERCENTAGE(0, 0.5))
            self.liveAngleText[i].setFontSize(18)
            self.liveAngleText[i].setTextSpacing(7)
            self.twinAngleText[i] = UiText(self.window, Constraints.ALIGN_TEXT_PERCENTAGE(0, 0.5))
            self.twinAngleText[i].setFontSize(18)
            self.twinAngleText[i].setTextSpacing(7)
            self.liveTextWrapper[i].addChild(self.liveAngleText[i])
            self.twinTextWrapper[i].addChild(self.twinAngleText[i])
            self.angleSlider[i] = UiSlider(self.window, Constraints.ALIGN_PERCENTAGE(0, 0.5, 1, 0.5))
            self.angleSlider[i].setRange(-pi, pi)
            self.angleSlider[i].setBaseColor((0,0,0))
            self.angleSlider[i].setSliderColor((0.8,0.8,0.8))
            self.angleSlider[i].setSliderPercentage(0.05)
            self.selecterWrappers[i].addChild(self.angleSlider[i])
        
        constraints = [
            COMPOUND(RELATIVE(T_X, 0.5, P_W), ABSOLUTE(T_X, padding)),
            COMPOUND(RELATIVE(T_Y, 0.8, P_H), ABSOLUTE(T_Y, padding)),
            COMPOUND(RELATIVE(T_W, 0.5, P_W), ABSOLUTE(T_W, -2*padding)),
            COMPOUND(RELATIVE(T_H, 0.1, P_H), ABSOLUTE(T_H, -2*padding)),
        ]
        self.sendBtn, self.sendBtnText = centeredTextButton(self.window, constraints)
        self.sendBtnText.setText('Execute')
        self.sendBtnText.setFontSize(20)
        self.sendBtnText.setTextSpacing(8)
        self.sendBtn.setDefaultColor((0,0,0))
        self.sendBtn.setHoverColor((0.1,0.1,0.1))
        self.sendBtn.setPressColor((0.2,0.2,0.2))
        self.armControlPanel.addChild(self.sendBtn)
        
        constraints = [
            COMPOUND(RELATIVE(T_X, 0, P_W), ABSOLUTE(T_X, padding)),
            COMPOUND(RELATIVE(T_Y, 0.8, P_H), ABSOLUTE(T_Y, padding)),
            COMPOUND(RELATIVE(T_W, 0.5, P_W), ABSOLUTE(T_W, -2*padding)),
            COMPOUND(RELATIVE(T_H, 0.1, P_H), ABSOLUTE(T_H, -2*padding)),
        ]
        self.unlinkBtn, self.unlinkBtnText = centeredTextButton(self.window, constraints)
        self.unlinkBtnText.setText('Unlink')
        self.unlinkBtnText.setFontSize(20)
        self.unlinkBtnText.setTextSpacing(8)
        self.unlinkBtn.setDefaultColor((0,0,0))
        self.unlinkBtn.setHoverColor((0.1,0.1,0.1))
        self.unlinkBtn.setPressColor((0.2,0.2,0.2))
        self.armControlPanel.addChild(self.unlinkBtn)

    def __createStreams(self):
        self.armStream = MJPEGStream('http://172.31.1.177:8080/?action=streams')

    def buildPlaneXY(self, x, y, z, dx, dy, vis):
        if vis==1:
            vertices_xy = [
                [x,y,z],[x+dx,y,z],[x,y+dy,z],
                [x,y+dy,z],[x+dx,y,z],[x+dx,y+dy,z],
            ]
        elif vis==2:
            vertices_xy = [
                [x,y,z],[x,y+dy,z],[x+dx,y,z],
                [x+dx,y,z],[x,y+dy,z],[x+dx,y+dy,z], 
            ]
        else:
            vertices_xy = [
                [x,y,z],[x+dx,y,z],[x,y+dy,z],
                [x,y+dy,z],[x+dx,y,z],[x+dx,y+dy,z],
                [x,y,z],[x,y+dy,z],[x+dx,y,z],
                [x+dx,y,z],[x,y+dy,z],[x+dx,y+dy,z],
            ]
        planexy = Model.fromVertices(vertices_xy)[0]
        plane = self.modelRenderer.addModel(planexy, createTransformationMatrix(0, 0, 0, 0, 0, 0))
        return plane
   
    def buildPlaneXZ(self, x, y, z, dx, dz, vis):
        if vis==1:
            vertices_xz = [
                [x,y,z],[x+dx,y,z],[x,y,z+dz],
                [x,y,z+dz],[x+dx,y,z],[x+dx,y,z+dz],
            ]
        elif vis==2:
            vertices_xz = [
                [x,y,z],[x,y,z+dz],[x+dx,y,z],
                [x+dx,y,z],[x,y,z+dz],[x+dx,y,z+dz],   
            ]
        else:
            vertices_xz = [
                [x,y,z],[x+dx,y,z],[x,y,z+dz],
                [x,y,z+dz],[x+dx,y,z],[x+dx,y,z+dz],
                [x,y,z],[x,y,z+dz],[x+dx,y,z],
                [x+dx,y,z],[x,y,z+dz],[x+dx,y,z+dz],
            ]
        planexz = Model.fromVertices(vertices_xz)[0]
        plane = self.modelRenderer.addModel(planexz, createTransformationMatrix(0, 0, 0, 0, 0, 0))
        return plane
    
    def buildPlaneYZ(self, x, y, z, dy, dz, vis):
        if vis==1:
            vertices_yz = [
                [x,y,z],[x,y+dy,z],[x,y,z+dz],
                [x,y,z+dz],[x,y+dy,z],[x,y+dy,z+dz],
            ]
        elif vis==2:
            vertices_yz = [
                [x,y,z],[x,y,z+dz],[x,y+dy,z],
                [x,y+dy,z],[x,y,z+dz],[x,y+dy,z+dz],   
            ]
        else:
            vertices_yz = [
                [x,y,z],[x,y+dy,z],[x,y,z+dz],
                [x,y,z+dz],[x,y+dy,z],[x,y+dy,z+dz],
                [x,y,z],[x,y,z+dz],[x,y+dy,z],
                [x,y+dy,z],[x,y,z+dz],[x,y+dy,z+dz],
            ]
        planeyz = Model.fromVertices(vertices_yz)[0] 
        plane = self.modelRenderer.addModel(planeyz, createTransformationMatrix(0, 0, 0, 0, 0, 0))
        return plane
    
    def buildPlaneFromPoints(self, point1, point2, point3, point4, vis):
        # Define vertices from the four input points
        # Visibility options for one way planes
        if vis==1:
            vertices = [
                point1, point2, point3,
                point3, point4, point1,
            ]
        elif vis==2:
            vertices = [
                point3, point2, point1,
                point1, point4, point3,
            ]            
        else:
            vertices = [
                point1, point2, point3,
                point3, point4, point1,
                point3, point2, point1,
                point1, point4, point3,
            ]
        # Create model object from vertices
        plane = Model.fromVertices(vertices)[0]
        # Add model object to model renderer and return handle to the model
        return self.modelRenderer.addModel(plane, createTransformationMatrix(0, 0, 0, 0, 0, 0))

    def buildWallPlan(self, wallplan):
        for wall in wallplan:
            point1 = (wall[0][0], wall[0][1], wall[2][0])
            point2 = (wall[1][0], wall[1][1], wall[2][0])
            point3 = (wall[1][0], wall[1][1], wall[2][1])
            point4 = (wall[0][0], wall[0][1], wall[2][1])
            self.planes.append(self.buildPlaneFromPoints(point1, point2, point3, point4,0))



    def __createRoom(self):
                #FLOOR
        self.planes.append(self.buildPlaneXY(0, 0, 0, 6, 2.5, 0)) #Floor
        self.modelRenderer.setColor(self.planes[0], (0.3, 0.3, 0.3, 1))

        w = 6
        d = 2.5
        h = 2.481
        banner_h = 0.5

        bar_w = 0.01
        self.planes.append(self.buildPlaneXY(w/2-bar_w/2,0,h-bar_w,bar_w,h,0))
        self.modelRenderer.setColor(self.planes[1], (0.3, 0.3, 0.3, 1))
        self.planes.append(self.buildPlaneXY(w/2-bar_w/2,0,h,bar_w,h,0))
        self.modelRenderer.setColor(self.planes[2], (0.3, 0.3, 0.3, 1))
        self.planes.append(self.buildPlaneYZ(w/2-bar_w/2,0,h-bar_w,h,bar_w,0))
        self.modelRenderer.setColor(self.planes[3], (0.3, 0.3, 0.3, 1))
        self.planes.append(self.buildPlaneYZ(w/2+bar_w/2,0,h-bar_w,h,bar_w,0))
        self.modelRenderer.setColor(self.planes[4], (0.3, 0.3, 0.3, 1))

        self.planes.append(self.buildPlaneXZ(w/2-bar_w/2,0,0,bar_w,h,0))
        self.modelRenderer.setColor(self.planes[5], (0.3, 0.3, 0.3, 1))
        self.planes.append(self.buildPlaneXZ(w/2+bar_w/2,0,0,bar_w,h,0))
        self.modelRenderer.setColor(self.planes[6], (0.3, 0.3, 0.3, 1))
        self.planes.append(self.buildPlaneYZ(w/2-bar_w/2,0,0,bar_w,h,0))
        self.modelRenderer.setColor(self.planes[7], (0.3, 0.3, 0.3, 1))
        self.planes.append(self.buildPlaneYZ(w/2+bar_w/2,0,0,bar_w,h,0))
        self.modelRenderer.setColor(self.planes[8], (0.3, 0.3, 0.3, 1))

         #New Lab
        wallplan = [
            ((0,0),(0,d),(0,h)),#LEFT WALL
            ((0,d),(w,d),(0,h)),#BACK WALL     
            ((w,0),(w,d),(0,h)),#RIGHT WALL 
            ((0,-0.001),(w,-0.001),(h-banner_h,h)),#FRONT PANEL

        ]
        self.buildWallPlan(wallplan)
        self.modelRenderer.setColor(self.planes[12], (0.8, 0.8, 0.8, 1))

    def __addFurniture(self):
        self.screenId = self.modelRenderer.addModel(Assets.SCREEN, createTransformationMatrix(0.01, 0.2, 1, 0, -90, 0))
        self.modelRenderer.setTexture(self.screenId, Assets.AMW_LEFT_TEX.texture)
        self.modelRenderer.setColor(self.screenId, (1,1,1,1))

        self.benches = [0]*1
        self.benches[0] = self.modelRenderer.addModel(Assets.KUKA_BASE, createTransformationMatrix(1, 1, 0.93, 0, 0, 0))

        self.barstool1 = self.modelRenderer.addModel(Assets.BAR_STOOL, createTransformationMatrix(1.5, 2, 0, 0, 0, 0))
        self.barstool2 = self.modelRenderer.addModel(Assets.BAR_STOOL, createTransformationMatrix(2.5, 2, 0, 0, 0, 0))
        # self.modelRenderer.setColor(self.barstool, (0,1,1,1))
        self.counter = self.modelRenderer.addModel(Assets.COUNTER, createTransformationMatrix(4, 0.5, 0, 0, 0, 0))
        # self.modelRenderer.setColor(self.counter, (1,0,1,1))
        
        self.table = self.modelRenderer.addModel(Assets.TABLE, createTransformationMatrix(2, 2, 0, 0, 0, 0))
        self.screenTV1 = self.modelRenderer.addModel(Assets.TVSCREEN, createTransformationMatrix(0.5, 2, 0, 0, 0, 90))
        self.screenTV2 = self.modelRenderer.addModel(Assets.TVSCREEN, createTransformationMatrix(5.5, 2, 0, 0, 0, 0))

    def __addRobot(self):
        Robot1_T_0_ , Robot1_T_i_ = T_KUKAiiwa14([0,0,0,pi/2,0,0,0])
        self.modelKukaData = {}
        self.modelKukaIds = []
        TRobot1_T_0_ , TRobot1_T_i_ = T_KUKAiiwa14(self.twinJoints)
        self.twinKukaData = {}
        self.twinKukaIds = []
        for i in range(0,8):
            mat = Robot1_T_0_[i].copy()
            x, y, z = 1, 1, 0.93
            self.modelKukaIds.append(self.modelRenderer.addModel(Assets.KUKA_IIWA14_MODEL[i], mat))
            self.modelRenderer.setColor(self.modelKukaIds[-1], (0.5, i/8, 1, 0.7))
            self.modelKukaData[self.modelKukaIds[-1]] = (x+0.2, y, z, i)

            mat = TRobot1_T_0_[i].copy()
            self.twinKukaIds.append(self.modelRenderer.addModel(Assets.KUKA_IIWA14_MODEL[i], mat))
            self.modelRenderer.setColor(self.twinKukaIds[-1], (1, 0.5, i/8, 0))
            self.twinKukaData[self.twinKukaIds[-1]] = (x+0.2, y, z, i)
        
        self.gripperId = self.modelRenderer.addModel(Assets.GRIPPER, Robot1_T_0_[7].copy())
        self.modelRenderer.setColor(self.gripperId, (0.5, 1, 1, 0.8))

        self.TgripperId = self.modelRenderer.addModel(Assets.GRIPPER, TRobot1_T_0_[7].copy())
        self.modelRenderer.setColor(self.TgripperId, (1, 0.5, 1, 0))

        self.forceVectorId = self.modelRenderer.addModel(Assets.POLE, np.identity(4))
        self.modelRenderer.setColor(self.forceVectorId, (0,0,0,0.8))

    def handleUiEvents(self, event):
        if event['action'] == 'release':
            if event['obj'] == self.recenterBtn:
                self.cameraTransform = [-0.7+5, -0.57+2, 1.5, -70.25, 0, 45]
            if event['obj'] == self.sendBtn:
                self.sendBtn.lock
                for i in range(len(self.twinJoints)):
                    self.opcuaTransmitterContainer.setValue(f'ns=24;s=R4c_Joi{i+1}', self.twinJoints[i]*180/pi, ua.VariantType.Double)
                self.opcuaTransmitterContainer.setValue(f'ns=24;s=R4c_ProgID', self.progid, ua.VariantType.Int32)
                self.progStartFlag = True
            if event['obj'] == self.unlinkBtn:
                self.matchLive = not self.matchLive
                self.unlinkBtnText.setText('unlink' if self.matchLive else 'link')
                self.__updateTwinColor()
            if event['obj'] == self.renderWindow:
                self.__handleSceneEvents(event)
        return
    
    def __handleSceneEvents(self, event):
        modelId = event['modelId']
        padding = 10
        self.panelWrapper.removeAllChildren()
        if modelId in self.twinKukaIds or modelId in self.modelKukaIds or modelId == self.gripperId or modelId == self.TgripperId:
            self.renderWindow.updateWidth(COMPOUND(RELATIVE(T_W, 0.7, P_W), ABSOLUTE(T_W, -2*padding)))
            self.panelWrapper.addChild(self.armControlPanel)
        else:
            self.renderWindow.updateWidth(COMPOUND(RELATIVE(T_W, 1, P_W), ABSOLUTE(T_W, -2*padding)))

    def absUpdate(self, delta):
        self.__moveCamera(delta)
        self.__updateStreams(delta)
        self.__updateJoints()
        self.__updateGuiText()
        self.__updateProgram()
        self.modelRenderer.setViewMatrix(createViewMatrix(*self.cameraTransform))
        return

    def __updateStreams(self, delta):
        self.armStream.updateImage(delta)
    
    def __updateProgram(self):
        if not self.opcuaReceiverContainer.getValue('ns=24;s=R4f_Ready', default=False)[0]:
            self.sendBtn.lock()
        if self.progStartFlag:
            self.sendBtn.lock()
            self.unlinkBtn.lock()
            self.sendBtnText.setText('Waiting')
            if self.__isTransmitClear():
                self.executingFlag = True
                self.progStartFlag = False
                self.opcuaTransmitterContainer.setValue('ns=24;s=R4c_Start', True, ua.VariantType.Boolean)
        elif self.executingFlag:
            self.sendBtn.lock()
            self.unlinkBtn.lock()
            self.sendBtnText.setText('Executing')
            if self.opcuaReceiverContainer.getValue('ns=24;s=R4c_ProgID', default=self.progid)[0] == 0:
                self.doneFlag = True
                self.executingFlag = False
        elif self.doneFlag:
            self.doneFlag = False
            self.sendBtn.unlock()
            self.unlinkBtn.unlock()
            self.matchLive = True
            self.unlinkBtnText.setText('Unlink')
            self.sendBtnText.setText('Execute')
            self.__updateTwinColor()
        elif self.opcuaReceiverContainer.getValue('ns=24;s=R4f_Ready', default=False)[0]:
            self.sendBtn.unlock()

    def __updateGuiText(self):
        for i in range(len(self.selecterWrappers)):
            self.liveAngleText[i].setText(f'Live: {int(self.jointsRad[i]*180/pi)}')
            if not self.matchLive:
                twinText = self.angleSlider[i].getValue()
                self.twinJoints[i] = float(twinText)
            else:
                self.angleSlider[i].setValue(self.twinJoints[i])
            self.twinAngleText[i].setText(f'Twin: {int(self.twinJoints[i]*180/pi)}')

    def __updateJoints(self):
        for i in range(7):
            if not self.opcuaReceiverContainer.hasUpdated(f'ns=24;s=R4d_Joi{i+1}'): continue
            self.jointsRad[i] = radians(self.opcuaReceiverContainer.getValue(f'ns=24;s=R4d_Joi{i+1}', default=0)[0])
        if self.opcuaReceiverContainer.hasUpdated('ns=24;s=R4d_ForX'):
            self.forceVector[0] = self.opcuaReceiverContainer.getValue('ns=24;s=R4d_ForX', default=0)[0]
        if self.opcuaReceiverContainer.hasUpdated('ns=24;s=R4d_ForY'):
            self.forceVector[1] = self.opcuaReceiverContainer.getValue('ns=24;s=R4d_ForY', default=0)[0]
        if self.opcuaReceiverContainer.hasUpdated('ns=24;s=R4d_ForZ'):
            self.forceVector[2] = self.opcuaReceiverContainer.getValue('ns=24;s=R4d_ForZ', default=0)[0]
        if self.matchLive:
            self.twinJoints = self.jointsRad.copy()
        Robot1_T_0_ , Robot1_T_i_ = T_KUKAiiwa14(self.jointsRad)
        for id in self.modelKukaIds:
            mat = Robot1_T_0_[self.modelKukaData[id][3]].copy()
            mat[0][3] += self.modelKukaData[id][0]*2/2
            mat[1][3] += self.modelKukaData[id][1]*2/2
            mat[2][3] += self.modelKukaData[id][2]*2/2
            self.modelRenderer.setTransformMatrix(id, mat)
        
        TRobot1_T_0_ , TRobot1_T_i_ = T_KUKAiiwa14(self.twinJoints)
        for id in self.twinKukaIds:
            mat = TRobot1_T_0_[self.twinKukaData[id][3]].copy()
            mat[0][3] += self.twinKukaData[id][0]*2/2
            mat[1][3] += self.twinKukaData[id][1]*2/2
            mat[2][3] += self.twinKukaData[id][2]*2/2
            self.modelRenderer.setTransformMatrix(id, mat)
        
        
        mat = Robot1_T_0_[7].copy()
        mat[0][3] += self.modelKukaData[self.modelKukaIds[7]][0]*2/2
        mat[1][3] += self.modelKukaData[self.modelKukaIds[7]][1]*2/2
        mat[2][3] += self.modelKukaData[self.modelKukaIds[7]][2]*2/2
        self.modelRenderer.setTransformMatrix(self.gripperId, mat)
        
        mat = TRobot1_T_0_[7].copy()
        mat[0][3] += self.twinKukaData[self.twinKukaIds[7]][0]*2/2
        mat[1][3] += self.twinKukaData[self.twinKukaIds[7]][1]*2/2
        mat[2][3] += self.twinKukaData[self.twinKukaIds[7]][2]*2/2
        self.modelRenderer.setTransformMatrix(self.TgripperId, mat)

        self.__updateForceVector(mat)
    
    def __updateForceVector(self, transform):
        forceMag = np.linalg.norm(self.forceVector)
        if forceMag < 3.5:
            self.modelRenderer.setColor(self.forceVectorId, (1,1,1,0))
            return
        
        forceTransform = vectorTransform(transform[:3,3], transform[:3,3]+2*self.forceVector, 1, upperLimit=100)
        self.modelRenderer.setColor(self.forceVectorId, (0,0,0,0.7))
        self.modelRenderer.setTransformMatrix(self.forceVectorId, forceTransform)

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

    def start(self):
        self.armStream.start()
        self.threadStopFlag = False

        if not self.dataThread.is_alive():
            self.dataThread = Opcua.createOpcuaReceiverThread(self.opcuaReceiverContainer, 'oct.tpc://172.31.1.236:4840/server/', 
                [
                    'ns=24;s=R4d_Joi1', 
                    'ns=24;s=R4d_Joi2', 
                    'ns=24;s=R4d_Joi3', 
                    'ns=24;s=R4d_Joi4', 
                    'ns=24;s=R4d_Joi5', 
                    'ns=24;s=R4d_Joi6', 
                    'ns=24;s=R4d_Joi7'
                ], lambda:self.threadStopFlag)
        if not self.forceThread.is_alive():
            self.forceThread = Opcua.createOpcuaReceiverThread(self.opcuaReceiverContainer, 'oct.tpc://172.31.1.236:4840/server/', 
                [
                    'ns=24;s=R4d_ForX', 
                    'ns=24;s=R4d_ForY', 
                    'ns=24;s=R4d_ForZ' 
                ], lambda:self.threadStopFlag)
        if not self.progControlThread.is_alive():
            self.progControlThread = Opcua.createOpcuaReceiverThread(self.opcuaReceiverContainer, 'oct.tpc://172.31.1.236:4840/server/', 
            [
                'ns=24;s=R4c_ProgID', 
                'ns=24;s=R4c_Start',    
                'ns=24;s=R4f_Ready', 
                'ns=24;s=R4f_End',  
            ], lambda:self.threadStopFlag)
        if not self.transmitter.is_alive():
            self.transmitter = Opcua.createOpcuaTransmitterThread(self.opcuaTransmitterContainer, 'oct.tpc://172.31.1.236:4840/server/', lambda:self.threadStopFlag)
        return
    
    def stop(self):
        self.armStream.stop()
        self.threadStopFlag = True
        return

    def __isTransmitClear(self):
        for i in range(len(self.twinJoints)):
            if self.opcuaTransmitterContainer.hasUpdated(f'ns=24;s=R4c_Joi{i+1}'):
                return False
        if self.opcuaTransmitterContainer.hasUpdated(f'ns=24;s=R4c_ProgID'):
            return False
        if self.opcuaReceiverContainer.getValue('ns=24;s=R4c_ProgID', default=0)[0] != self.progid:
            return False
        if not self.opcuaReceiverContainer.getValue('ns=24;s=R4f_Ready', default=False)[0]:
            return False
        return True

    def __updateTwinColor(self):
        for id in self.twinKukaIds:
            color = self.modelRenderer.getData(id)['color']
            self.modelRenderer.setColor(id, (*color[0:3], 0 if self.matchLive else 0.7))
        color = self.modelRenderer.getData(self.TgripperId)['color']
        self.modelRenderer.setColor(self.TgripperId, (*color[0:3], 0 if self.matchLive else 0.8))

