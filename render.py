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

from mathHelper import *
from model import *

FOV = 60
NEAR_PLANE = 0.1;
FAR_PLANE = 1000;

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
display = (800,800)
window = pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

Assets.init()

GL.glEnable(GL.GL_CULL_FACE)
GL.glEnable(GL.GL_DEPTH_TEST)
GL.glCullFace(GL.GL_BACK)

clock = pygame.time.Clock()

Assets.KUKA_MODEL
Assets.KUKA_MODEL[0].setColor([1.0, 0.0, 0.0])
Assets.KUKA_MODEL[1].setColor([1.0, 0.0, 0.0])
Assets.KUKA_MODEL[2].setColor([1.0, 1.0, 0.0])
Assets.KUKA_MODEL[3].setColor([0.0, 0.0, 1.0])
Assets.KUKA_MODEL[4].setColor([1.0, 0.0, 1.0])
Assets.KUKA_MODEL[5].setColor([0.0, 1.0, 1.0])
Assets.KUKA_MODEL[6].setColor([1.0, 1.0, 1.0])
Assets.KUKA_MODEL[7].setColor([0.5, 0.5, 0.5])

for obj in Assets.KUKA_MODEL:
    obj.setProjectionMatrix(createProjectionMatrix(800, 800, FOV, NEAR_PLANE, FAR_PLANE))

rx = 0
ry = 0
rz = 0

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
        rx += 13*deltaT
        ry += 17*deltaT
        rz += 19*deltaT

    GL.glClear(GL.GL_COLOR_BUFFER_BIT|GL.GL_DEPTH_BUFFER_BIT)
    #############################Start Render#############################

    q = np.array([0,0,0,pi/2,0,0,0])
    Robot1_T_0_ , Robot1_T_i_ = T_KUKAiiwa14(q)
    for i in range(len(Assets.KUKA_MODEL)):
        Assets.KUKA_MODEL[i].setTransformMatrix(Robot1_T_0_[i])
        Assets.KUKA_MODEL[i].setViewMatrix(createViewMatrix(0, 0.5, 2, -45, 0, rz))
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





