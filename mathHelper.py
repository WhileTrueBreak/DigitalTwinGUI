from math import *
import numpy as np
import functools

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm

def createProjectionMatrix(width, height, FOV, NEAR_PLANE, FAR_PLANE):
    aspectRatio = 1
    if height != 0:
        aspectRatio = width/height
    yScale = (float) ((1/tan(radians(FOV/2)))*aspectRatio)
    xScale = 0
    if aspectRatio != 0:
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
    rrotx = radians(rotx)
    rroty = radians(roty)
    rrotz = radians(rotz)
    trans = createTransformationMatrix(-x, -y, -z, 0, 0, 0)
    rot = createTransformationMatrix(0, 0, 0, rotx, roty, rotz)
    return rot.dot(trans)

def unitVector(vector):
    return vector / np.linalg.norm(vector)

def angleBetween(v1, v2):
    v1_u = unitVector(v1)
    v2_u = unitVector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def vectorTransform(p1, p2, thickness, upperLimit=10000000):
    vector = p2-p1
    mag = np.linalg.norm(vector)
    rotMat = np.identity(4)
    if mag != 0:
        z0 = vector/mag
        x0 = normalize(np.cross(z0,[0,0,1]))
        rot = np.identity(3)
        if np.linalg.norm(x0) != 0:
            y0 = normalize(np.cross(z0,x0))
            rot = np.column_stack((x0,y0,z0))
        rotMat[:3,:3] = rot
        rotMat[:3,3] = p1

    scaleTMAT = np.identity(4)
    scaleTMAT[0,0] = thickness
    scaleTMAT[1,1] = thickness
    scaleTMAT[2,2] = min(mag,upperLimit)
    return rotMat.dot(scaleTMAT)









