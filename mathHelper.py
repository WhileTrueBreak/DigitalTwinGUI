from math import *
import numpy as np
import functools

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm

def createProjectionMatrix(width, height, FOV, NEAR_PLANE, FAR_PLANE):
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

def createTransformationMatrix(x, y, z, rotx, roty, rotz):
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
    return createTransformationMatrix(-x, -y, -z, rotx, roty, rotz)


