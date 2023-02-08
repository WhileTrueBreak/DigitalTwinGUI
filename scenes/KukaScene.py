from ui.uiElement import *
from ui.uiHelper import *
from constraintManager import *
from scenes.scene import *
from mathHelper import *
from opcua import *

import pygame

from math import *

from asyncua import Client, ua
import asyncio
import asyncio

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

        self.threadStopFlag = False
        self.dataQueue = Queue()
        return

    def createUi(self):
        padding = 20
        constraints = [
            ABSOLUTE(T_X, padding),
            ABSOLUTE(T_Y, padding),
            COMPOUND(RELATIVE(T_W, 0.5, P_W), ABSOLUTE(T_W, -2*padding)),
            COMPOUND(RELATIVE(T_H, 1, P_H), ABSOLUTE(T_H, -2*padding)),
        ]
        self.renderWindow = Ui3DScene(self.window, constraints)
        self.modelRenderer = self.renderWindow.getRenderer()
        self.sceneWrapper.addChild(self.renderWindow)
        self.addModels()
        return
    
    def addModels(self):
        Robot1_T_0_ , Robot1_T_i_ = T_KUKAiiwa14([0,0,0,pi/2,0,0,0])
        self.modelData = {}
        self.modelIds = []
        for i in range(8):
            mat = Robot1_T_0_[i].copy()
            self.modelIds.append(self.modelRenderer.addModel(Assets.KUKA_MODEL[i], mat))
            self.modelRenderer.setColor(self.modelIds[-1], [1, i/7, 0, 1])
            self.modelData[self.modelIds[-1]] = (0, 0, 0, i)

    def handleUiEvents(self, event):
        return
    
    def absUpdate(self, delta):
        self.moveCamera(delta)
        self.updateJoints()
        self.modelRenderer.setViewMatrix(createViewMatrix(*self.cameraTransform))
        return
    
    def updateJoints(self):
        if not self.dataQueue.empty():
            data = self.dataQueue.get()
            while not self.dataQueue.empty():
                data = self.dataQueue.get()
            self.jointsRad[0] = radians(data['ns=24;s=R4d_Joi1'])
            self.jointsRad[1] = radians(data['ns=24;s=R4d_Joi2'])
            self.jointsRad[2] = radians(data['ns=24;s=R4d_Joi3'])
            self.jointsRad[3] = radians(data['ns=24;s=R4d_Joi4'])
            self.jointsRad[4] = radians(data['ns=24;s=R4d_Joi5'])
            self.jointsRad[5] = radians(data['ns=24;s=R4d_Joi6'])
            self.jointsRad[6] = radians(data['ns=24;s=R4d_Joi7'])
        Robot1_T_0_ , Robot1_T_i_ = T_KUKAiiwa14(self.jointsRad)
        for id in self.modelIds:
            mat = Robot1_T_0_[self.modelData[id][3]].copy()
            mat[0][3] += self.modelData[id][0]*2/2
            mat[1][3] += self.modelData[id][1]*2/2
            mat[2][3] += self.modelData[id][2]*2/2
            self.modelRenderer.setTransformMatrix(id, mat)
    
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
        deltaPos = [x*delta*2 for x in normalize(deltaPos)]
        radPitch = radians(self.cameraTransform[3])
        radYaw = radians(self.cameraTransform[5])

        yawX = deltaPos[0]*cos(radYaw)+deltaPos[2]*sin(radYaw)
        yawY = deltaPos[2]*cos(radYaw)-deltaPos[0]*sin(radYaw)

        self.cameraTransform[0] += yawX+deltaPos[1]*sin(radPitch)*sin(radYaw)
        self.cameraTransform[1] += yawY+deltaPos[1]*sin(radPitch)*cos(radYaw)
        self.cameraTransform[2] += deltaPos[1]*cos(radPitch)-deltaPos[2]*sin(radPitch)

    def start(self):
        self.threadStopFlag = False
        self.dataThread = Opcua.createOpcuaThread(self.dataQueue, ['ns=24;s=R4d_Joi1', 
                                                                   'ns=24;s=R4d_Joi2', 
                                                                   'ns=24;s=R4d_Joi3', 
                                                                   'ns=24;s=R4d_Joi4', 
                                                                   'ns=24;s=R4d_Joi5', 
                                                                   'ns=24;s=R4d_Joi6', 
                                                                   'ns=24;s=R4d_Joi7'], lambda:self.threadStopFlag)
        return
    
    def stop(self):
        self.threadStopFlag = True
        return

