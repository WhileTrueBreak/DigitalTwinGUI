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

from model import *

FOV = 60
NEAR_PLANE = 0.1;
FAR_PLANE = 1000;

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm

def createProjectionMatrix():
    width = 800
    height = 800
    aspectRatio = width/height
    yScale = (float) ((1/tan(radians(FOV/2)))*aspectRatio)
    xScale = yScale/aspectRatio
    frustumLength = FAR_PLANE-NEAR_PLANE
    
    projectionMatrix = np.zeros((4,4))
    projectionMatrix[0][0] = xScale
    projectionMatrix[1][1] = yScale
    projectionMatrix[2][2] = -((FAR_PLANE+NEAR_PLANE)/frustumLength)
    projectionMatrix[2][3] = -1
    projectionMatrix[3][2] = -((2*FAR_PLANE*NEAR_PLANE)/frustumLength)
    projectionMatrix[3][3] = 0
    return projectionMatrix

def createTranslationMatrix(x, y, z, rotx, roty, rotz):
    rotx = radians(rotx)
    roty = radians(roty)
    rotz = radians(rotz)
    rotmx = np.identity(3)
    rotmx[1][1] = cos(rotx)
    rotmx[1][2] = -sin(rotx)
    rotmx[2][1] = sin(rotx)
    rotmx[2][2] = cos(rotx)
    rotmy = np.identity(3)
    rotmy[0][0] = cos(roty)
    rotmy[0][2] = sin(roty)
    rotmy[2][0] = -sin(roty)
    rotmy[2][2] = cos(roty)
    rotmz = np.identity(3)
    rotmz[1][1] = cos(rotz)
    rotmz[1][0] = sin(rotz)
    rotmz[0][1] = -sin(rotz)
    rotmz[0][0] = cos(rotz)
    rotm = functools.reduce(np.dot, [rotmx,rotmy,rotmz])

    tmat = np.pad(rotm, [(0, 1), (0, 1)], mode='constant', constant_values=0)

    tmat[0][3] = x
    tmat[1][3] = y
    tmat[2][3] = z
    tmat[3][3] = 1
    return tmat

def createViewMatrix(x, y, z, rotx, roty, rotz):
    return createTranslationMatrix(-x, -y, -z, rotx, roty, rotz)

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

objs = []
objs.append(Model('res/models/link_0.stl'))
objs[-1].setColor([1, 0, 0])
objs.append(Model('res/models/link_1.stl'))
objs[-1].setColor([0, 1, 0])
objs.append(Model('res/models/link_2.stl'))
objs[-1].setColor([1, 1, 0])
objs.append(Model('res/models/link_3.stl'))
objs[-1].setColor([0, 0, 1])
objs.append(Model('res/models/link_4.stl'))
objs[-1].setColor([1, 0, 1])
objs.append(Model('res/models/link_5.stl'))
objs[-1].setColor([0, 1, 1])
objs.append(Model('res/models/link_6.stl'))
objs[-1].setColor([1, 1, 1])
objs.append(Model('res/models/link_7.stl'))
objs[-1].setColor([0, 0, 0])

for obj in objs:
    obj.setProjectionMatrix(createProjectionMatrix())

# obj = Model('res/models/teapot.stl')
# obj.setProjectionMatrix(createProjectionMatrix())

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
    q = np.array([0,0,0,0,0,0,0])
    Robot1_T_0_ , Robot1_T_i_ = T_KUKAiiwa14(q)
    for i in range(len(objs)):
        # print(Robot1_T_0_[i])
        objs[i].setTransformMatrix(Robot1_T_0_[i])
        objs[i].setViewMatrix(createViewMatrix(0, 0.5, 2, -45, 0, rz))
        # objs[i].setTransformMatrix(createTranslationMatrix(0,0,-3,0,0,0))
        objs[i].render()

    ############################# End Render #############################
    pygame.display.flip()

    deltaT = (start - end)/1000000000
    secTimer += deltaT
    frames += 1
    if secTimer >= 1:
        print(f'fps: {frames}')
        secTimer -= 1
        frames = 0





