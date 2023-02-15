from ui.uiElement import *
from ui.uiHelper import *
from constraintManager import *
from scenes.scene import *
from mathHelper import *
from opcua import *

from math import *
import random

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

class KukaScene(Scene):
    
    def __init__(self, window, name):
        super().__init__(window, name)
        self.cameraTransform = [-0.7, -0.57, 1.0, -70.25, 0, 45]

        self.jointsRad = [0,0,0,0,0,0,0]

        self.threadStopFlag = True
        self.opcuaContainer = OpcuaContainer()
        self.dataThread = Opcua.createOpcuaThread(self.opcuaContainer, 'oct.tpc://172.31.1.236:4840/server/', 
            [
                'ns=24;s=R4d_Joi1', 
                'ns=24;s=R4d_Joi2', 
                'ns=24;s=R4d_Joi3', 
                'ns=24;s=R4d_Joi4', 
                'ns=24;s=R4d_Joi5', 
                'ns=24;s=R4d_Joi6', 
                'ns=24;s=R4d_Joi7' 
            ], lambda:self.threadStopFlag)
        return

    def createUi(self):
        padding = 20
        constraints = [
            ABSOLUTE(T_X, padding),
            ABSOLUTE(T_Y, padding),
            COMPOUND(RELATIVE(T_W, 1, P_W), ABSOLUTE(T_W, -2*padding)),
            COMPOUND(RELATIVE(T_H, 1, P_H), ABSOLUTE(T_H, -2*padding)),
        ]
        self.renderWindow = Ui3DScene(self.window, constraints)
        self.modelRenderer = self.renderWindow.getRenderer()
        self.sceneWrapper.addChild(self.renderWindow)
        self.addModels()

        padding = 10
        constraints = [
            ABSOLUTE(T_X, padding),
            ABSOLUTE(T_Y, padding),
            ABSOLUTE(T_W, 30),
            RELATIVE(T_H, 1, T_W)
        ]
        self.recenterBtn, self.recenterText = centeredTextButton(self.window, constraints)
        self.recenterText.setText('RE')
        self.recenterText.setFontSize(20)
        self.recenterText.setTextSpacing(20)
        self.recenterText.setTextColor((1, 1, 1))
        self.recenterBtn.setDefaultColor((0, 0, 0))
        self.recenterBtn.setHoverColor((0.1, 0.1, 0.1))
        self.recenterBtn.setPressColor((1, 0, 0))
        self.renderWindow.addChild(self.recenterBtn)
        return
    
    def addModels(self):
        Robot1_T_0_ , Robot1_T_i_ = T_KUKAiiwa14([0,0,0,pi/2,0,0,0])
        self.modelKukaData = {}
        self.modelKukaIds = []
        for i in range(0,8):
            mat = Robot1_T_0_[i].copy()
            self.modelKukaIds.append(self.modelRenderer.addModel(Assets.KUKA_IIWA14_MODEL[i], mat))
            self.modelRenderer.setColor(self.modelKukaIds[-1], (0.5, i/8, 1, 0.7))
            self.modelKukaData[self.modelKukaIds[-1]] = (0, 0, 0, i)
        self.gripperId = self.modelRenderer.addModel(Assets.GRIPPER, Robot1_T_0_[7].copy())

        self.modelRenderer.setColor(self.gripperId, (0.5, 1, 1, 0.8))

        self.tubeIds = [0]*2
        self.tubeIds[0] = self.modelRenderer.addModel(Assets.TUBE_OUTSIDE, createTransformationMatrix(-0.134,0.805,0.0225,0,0,0))
        self.modelRenderer.setColor(self.tubeIds[0], (0.8, 0.8, 0, 1))
        self.tubeIds[1] = self.modelRenderer.addModel(Assets.TUBE_INSIDE, createTransformationMatrix(-0.134,0.805,0.0225,0,0,0))
        self.modelRenderer.setColor(self.tubeIds[1], (0.6, 0.6, 0.6, 1))

        self.tableIds = [0]*2
        self.tableIds[0] = self.modelRenderer.addModel(Assets.TABLES[2], createTransformationMatrix(0.5,1.6,-0.06625,0,0,0))
        self.modelRenderer.setColor(self.tableIds[0], (0.7, 0.7, 0.7, 1))
        self.tableIds[1] = self.modelRenderer.addModel(Assets.KUKA_BASE, np.identity(4))
        self.modelRenderer.setColor(self.tableIds[1], (0.7, 0.7, 0.7, 1))

        # self.floorId = self.modelRenderer.addModel(Assets.FLOOR, np.identity(4))
        # self.modelRenderer.setColor(self.floorId, (0.5, 0.5, 0.5, 1))

    def handleUiEvents(self, event):
        if event['action'] == 'release':
            if event['obj'] != self.recenterBtn: return
            self.cameraTransform = [-0.7, -0.57, 1.0, -70.25, 0, 45]
        return
    
    def absUpdate(self, delta):
        self.moveCamera(delta)
        self.updateJoints()
        self.modelRenderer.setViewMatrix(createViewMatrix(*self.cameraTransform))
        return
    
    def updateJoints(self):
        if self.opcuaContainer.hasUpdated():
            self.jointsRad[0] = radians(self.opcuaContainer.getValue('ns=24;s=R4d_Joi1', default=0))
            self.jointsRad[1] = radians(self.opcuaContainer.getValue('ns=24;s=R4d_Joi2', default=0))
            self.jointsRad[2] = radians(self.opcuaContainer.getValue('ns=24;s=R4d_Joi3', default=0))
            self.jointsRad[3] = radians(self.opcuaContainer.getValue('ns=24;s=R4d_Joi4', default=0))
            self.jointsRad[4] = radians(self.opcuaContainer.getValue('ns=24;s=R4d_Joi5', default=0))
            self.jointsRad[5] = radians(self.opcuaContainer.getValue('ns=24;s=R4d_Joi6', default=0))
            self.jointsRad[6] = radians(self.opcuaContainer.getValue('ns=24;s=R4d_Joi7', default=0))
        Robot1_T_0_ , Robot1_T_i_ = T_KUKAiiwa14(self.jointsRad)
        for id in self.modelKukaIds:
            mat = Robot1_T_0_[self.modelKukaData[id][3]].copy()
            mat[0][3] += self.modelKukaData[id][0]*2/2
            mat[1][3] += self.modelKukaData[id][1]*2/2
            mat[2][3] += self.modelKukaData[id][2]*2/2
            self.modelRenderer.setTransformMatrix(id, mat)
        mat = Robot1_T_0_[7].copy()
        mat[0][3] += self.modelKukaData[7][0]*2/2
        mat[1][3] += self.modelKukaData[7][1]*2/2
        mat[2][3] += self.modelKukaData[7][2]*2/2
        self.modelRenderer.setTransformMatrix(self.gripperId, mat)
    
    def moveCamera(self, delta):
        if self.window.getKeyState(K_j):
            self.cameraTransform[5] -= 90*delta
        if self.window.getKeyState(K_l):
            self.cameraTransform[5] += 90*delta
        if self.window.getKeyState(K_i):
            self.cameraTransform[3] += 90*delta
        if self.window.getKeyState(K_k):
            self.cameraTransform[3] -= 90*delta
        
        deltaPos = [0,0,0]
        if self.window.getKeyState(K_a): #left
            deltaPos[0] -= 1
        if self.window.getKeyState(K_d): #right
            deltaPos[0] += 1
        if self.window.getKeyState(K_w): #forward
            deltaPos[1] -= 1
        if self.window.getKeyState(K_s): #back
            deltaPos[1] += 1
        if self.window.getKeyState(K_LALT): #down
            deltaPos[2] -= 1
        if self.window.getKeyState(K_SPACE): #up
            deltaPos[2] += 1
        deltaPos = [x*delta for x in normalize(deltaPos)]
        radPitch = radians(self.cameraTransform[3])
        radYaw = radians(self.cameraTransform[5])

        yawX =  deltaPos[0]*cos(radYaw)#+deltaPos[2]*sin(radYaw)
        yawY =  -deltaPos[0]*sin(radYaw)#+deltaPos[2]*cos(radYaw)

        self.cameraTransform[0] += yawX-deltaPos[1]*sin(radYaw)#*sin(radPitch)
        self.cameraTransform[1] += yawY-deltaPos[1]*cos(radYaw)#*sin(radPitch)
        self.cameraTransform[2] += -deltaPos[2]*sin(radPitch)#+deltaPos[1]*cos(radPitch)

    def start(self):
        self.threadStopFlag = False
        if self.dataThread.is_alive(): return
        self.dataThread = Opcua.createOpcuaThread(self.opcuaContainer, 'oct.tpc://172.31.1.236:4840/server/', 
            [
                'ns=24;s=R4d_Joi1', 
                'ns=24;s=R4d_Joi2', 
                'ns=24;s=R4d_Joi3', 
                'ns=24;s=R4d_Joi4', 
                'ns=24;s=R4d_Joi5', 
                'ns=24;s=R4d_Joi6', 
                'ns=24;s=R4d_Joi7'
            ], lambda:self.threadStopFlag)
        return
    
    def stop(self):
        self.threadStopFlag = True
        return



