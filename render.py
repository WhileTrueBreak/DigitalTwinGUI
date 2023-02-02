import nest_asyncio
nest_asyncio.apply()

import pygame
from pygame.locals import *
from OpenGL import GL
from OpenGL import GLU
import matplotlib.cm
from vectors import *
from math import *
import numpy as np
from stl import mesh
from asset import *
import functools
import time

import asyncio
from opcua import Opcua

from mathHelper import *
from model import *


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

async def updateJoints(client):
    JOINTS[0] = await client.getValue('ns=24;s=R4c_Joi1;')
    JOINTS[1] = await client.getValue('ns=24;s=R4c_Joi2;')
    JOINTS[2] = await client.getValue('ns=24;s=R4c_Joi3;')
    JOINTS[3] = await client.getValue('ns=24;s=R4c_Joi4;')
    JOINTS[4] = await client.getValue('ns=24;s=R4c_Joi5;')
    JOINTS[5] = await client.getValue('ns=24;s=R4c_Joi6;')
    JOINTS[6] = await client.getValue('ns=24;s=R4c_Joi7;')
    
pygame.init()
display = (1600,1000)
window = pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

Assets.init()

print('\n'*10)

GL.glEnable(GL.GL_CULL_FACE)
GL.glEnable(GL.GL_DEPTH_TEST)
GL.glCullFace(GL.GL_BACK)

clock = pygame.time.Clock()

Assets.KUKA_MODEL
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

opcua = Opcua()

rot = 0

secTimer = 0
frames = 0
start = time.time_ns()
end = start
deltaT = 0

while True:
    end = start
    start = time.time_ns()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    if deltaT != 0:
        rot += 19*deltaT

    GL.glClear(GL.GL_COLOR_BUFFER_BIT|GL.GL_DEPTH_BUFFER_BIT)
    #############################Start Update#############################
    asyncio.run(updateJoints(opcua))
    jointsRad = [radians(a) for a in JOINTS]
    q = np.array(jointsRad)
    Robot1_T_0_ , Robot1_T_i_ = T_KUKAiiwa14(q)

    #############################Start Render#############################
    for i in range(len(Assets.KUKA_MODEL)):
        Assets.KUKA_MODEL[i].setTransformMatrix(Robot1_T_0_[i])
        Assets.KUKA_MODEL[i].setViewMatrix(createViewMatrix(0, 0.5, 2, -50, 0, rot))
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





