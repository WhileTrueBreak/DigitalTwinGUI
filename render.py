import nest_asyncio
nest_asyncio.apply()

import pygame
from pygame.locals import *
from OpenGL import GL
from OpenGL import GLU
from math import *
import numpy as np
from asset import *
import time

from queue import Queue

import asyncio
from opcua import Opcua

from mathHelper import *
from model import *

import signal

FOV = 60
NEAR_PLANE = 0.1;
FAR_PLANE = 1000;

JOINTS = [0]*7

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

pygame.init()
display = (1600,1000)
window = pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

Assets.init()

print('\n'*10)

GL.glEnable(GL.GL_CULL_FACE)
GL.glEnable(GL.GL_DEPTH_TEST)
GL.glCullFace(GL.GL_BACK)

Assets.KUKA_MODEL[0].setColor([0.5, 0.5, 0.5])
Assets.KUKA_MODEL[1].setColor([0.5, 0.5, 0.5])
Assets.KUKA_MODEL[2].setColor([0.9, 0.4, 0.0])
Assets.KUKA_MODEL[3].setColor([0.5, 0.5, 0.5])
Assets.KUKA_MODEL[4].setColor([0.5, 0.5, 0.5])
Assets.KUKA_MODEL[5].setColor([0.9, 0.4, 0.0])
Assets.KUKA_MODEL[6].setColor([0.5, 0.5, 0.5])
Assets.KUKA_MODEL[7].setColor([0.8, 0.8, 0.8])

for obj in Assets.KUKA_MODEL:
    obj.setProjectionMatrix(createProjectionMatrix(*window.get_size(), FOV, NEAR_PLANE, FAR_PLANE))

rot = 0

secTimer = 0
frames = 0
start = time.time_ns()
end = start
deltaT = 0

threadStopFlag = False

dataQueue = Queue()
dataThread = Opcua.createOpcuaThread(dataQueue, ['ns=24;s=R4d_Joi1', 
                                                 'ns=24;s=R4d_Joi2', 
                                                 'ns=24;s=R4d_Joi3', 
                                                 'ns=24;s=R4d_Joi4', 
                                                 'ns=24;s=R4d_Joi5', 
                                                 'ns=24;s=R4d_Joi6', 
                                                 'ns=24;s=R4d_Joi7'], lambda:threadStopFlag)

jointsRad = np.array([0]*7, dtype='float32')

def handler(signum, frame):
    pygame.quit()
    threadStopFlag = True
    dataThread.join()
    quit()

signal.signal(signal.SIGINT, handler)

while True:
    end = start
    start = time.time_ns()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            threadStopFlag = True
            dataThread.join()
            quit()

    if deltaT != 0:
        rot += 19*deltaT

    GL.glClear(GL.GL_COLOR_BUFFER_BIT|GL.GL_DEPTH_BUFFER_BIT)
    #############################Start Update#############################
    if not dataQueue.empty():
        data = dataQueue.get()
        while not dataQueue.empty():
            data = dataQueue.get()
        jointsRad[0] = radians(data['ns=24;s=R4d_Joi1'])
        jointsRad[1] = radians(data['ns=24;s=R4d_Joi2'])
        jointsRad[2] = radians(data['ns=24;s=R4d_Joi3'])
        jointsRad[3] = radians(data['ns=24;s=R4d_Joi4'])
        jointsRad[4] = radians(data['ns=24;s=R4d_Joi5'])
        jointsRad[5] = radians(data['ns=24;s=R4d_Joi6'])
        jointsRad[6] = radians(data['ns=24;s=R4d_Joi7'])
    Robot1_T_0_ , Robot1_T_i_ = T_KUKAiiwa14(jointsRad)

    #############################Start Render#############################

    for x in range(-3,3):
        for y in range(-3,3):
            for i in range(len(Assets.KUKA_MODEL)):
                t = Robot1_T_0_[i].copy()
                t[0][3] += x*2/3
                t[1][3] += y*2/3
                Assets.KUKA_MODEL[i].setTransformMatrix(t)
                Assets.KUKA_MODEL[i].setViewMatrix(createViewMatrix(0, 0.5, 2, -60, 0, 45))
                Assets.KUKA_MODEL[i].render()


    ############################# End Render #############################
    pygame.display.flip()

    deltaT = (start - end)/1000000000
    secTimer += deltaT
    frames += 1
    if secTimer >= 1:
        print(f'fps: {frames}')
        secTimer -= 1
        frames = 0


