from asset import *
from mathHelper import *

from math import *

import pygame
from pygame.locals import *

import OpenGL.GL as GL
import numpy as np
import ctypes

cameraTransform = [-2, 0, 0.5, 0, 20, 0]
keyState = {}

def getKeyState(key):
    if not key in keyState:
        return False
    return keyState[key]

def moveCamera(delta):
    if getKeyState(K_j):
        cameraTransform[5] -= 90*delta
    if getKeyState(K_l):
        cameraTransform[5] += 90*delta
    if getKeyState(K_i):
        cameraTransform[3] += 90*delta
    if getKeyState(K_k):
        cameraTransform[3] -= 90*delta
    
    deltaPos = [0,0,0]
    if getKeyState(K_a): #left
        deltaPos[0] -= 1
    if getKeyState(K_d): #right
        deltaPos[0] += 1
    if getKeyState(K_w): #forward
        deltaPos[1] -= 1
    if getKeyState(K_s): #back
        deltaPos[1] += 1
    if getKeyState(K_LALT): #down
        deltaPos[2] -= 1
    if getKeyState(K_SPACE): #up
        deltaPos[2] += 1
    deltaPos = [x*delta for x in normalize(deltaPos)]
    radPitch = radians(cameraTransform[3])
    radYaw = radians(cameraTransform[5])

    yawX = deltaPos[0]*cos(radYaw)+deltaPos[2]*sin(radYaw)
    yawY = deltaPos[2]*cos(radYaw)-deltaPos[0]*sin(radYaw)

    cameraTransform[0] += yawX+deltaPos[1]*sin(radPitch)*sin(radYaw)
    cameraTransform[1] += yawY+deltaPos[1]*sin(radPitch)*cos(radYaw)
    cameraTransform[2] += deltaPos[1]*cos(radPitch)-deltaPos[2]*sin(radPitch)

##########################

pygame.init()
display_flags = pygame.DOUBLEBUF | pygame.OPENGL
screen = pygame.display.set_mode((800, 800), display_flags)
pygame.display.set_caption('title')
dim = screen.get_size()

Assets.init()
##########################

quadVertices = np.array([
    [-1,-1,-1, 0, 0],
    [ 1,-1,-1, 1, 0],
    [ 1, 1,-1, 1, 1],
    [ 1, 1,-1, 1, 1],
    [-1, 1,-1, 0, 1],
    [-1,-1,-1, 0, 0],
], dtype='float32')

quadVAO = GL.glGenVertexArrays(1)
quadVBO = GL.glGenBuffers(1)
GL.glBindVertexArray(quadVAO)
GL.glBindBuffer(GL.GL_ARRAY_BUFFER, quadVBO)
GL.glBufferData(GL.GL_ARRAY_BUFFER, quadVertices.nbytes, quadVertices, GL.GL_DYNAMIC_DRAW)
GL.glEnableVertexAttribArray(0)
GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 5 * 4, ctypes.c_void_p(0*4))
GL.glEnableVertexAttribArray(1)
GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 5 * 4, ctypes.c_void_p(3*4))
GL.glBindVertexArray(0)

opaqueFBO = GL.glGenFramebuffers(1)
transparentFBO = GL.glGenFramebuffers(1)

opaqueTexture = GL.glGenTextures(1)
GL.glBindTexture(GL.GL_TEXTURE_2D, opaqueTexture)
GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA16F, dim[0], dim[1], 0, GL.GL_RGBA, GL.GL_HALF_FLOAT, None)
GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

depthTexture = GL.glGenTextures(1)
GL.glBindTexture(GL.GL_TEXTURE_2D, depthTexture)
GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_DEPTH_COMPONENT, dim[0], dim[1], 0, GL.GL_DEPTH_COMPONENT, GL.GL_FLOAT, None)
GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, opaqueFBO)
GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, opaqueTexture, 0)
GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_DEPTH_ATTACHMENT, GL.GL_TEXTURE_2D, depthTexture, 0)
GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

accumTexture = GL.glGenTextures(1)
GL.glBindTexture(GL.GL_TEXTURE_2D, accumTexture)
GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA16F, dim[0], dim[1], 0, GL.GL_RGBA, GL.GL_HALF_FLOAT, None)
GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

revealTexture = GL.glGenTextures(1)
GL.glBindTexture(GL.GL_TEXTURE_2D, revealTexture)
GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_R8, dim[0], dim[1], 0, GL.GL_RED, GL.GL_FLOAT, None)
GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, transparentFBO)
GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, accumTexture, 0)
GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT1, GL.GL_TEXTURE_2D, revealTexture, 0)
GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_DEPTH_ATTACHMENT, GL.GL_TEXTURE_2D, depthTexture, 0)

transparentDrawBuffers = (GL.GL_COLOR_ATTACHMENT0, GL.GL_COLOR_ATTACHMENT1)
GL.glDrawBuffers(transparentDrawBuffers)

redModelMat = createTransformationMatrix(0,0,2,0,0,0)
greenModelMat = createTransformationMatrix(0,0,1,0,0,0)
blueModelMat = createTransformationMatrix(0,0,0,0,0,0)

accumClear = np.array([0,0,0,0], dtype='float32')
revealClear = np.array([1,0,0,0], dtype='float32')

delta = 1
timeCounter = 0
frames = 0
start = time.time_ns()

running = True
while running:
    end = start
    start = time.time_ns()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            keyState[event.key] = True
        if event.type == pygame.KEYUP:
            keyState[event.key] = False
    moveCamera(delta)
    ####################

    projection = createProjectionMatrix(dim[0], dim[1], 80, 0.5, 1000).T
    view = createViewMatrix(*cameraTransform).T
    vp = np.dot(view, projection)

    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glDepthFunc(GL.GL_LESS)
    GL.glDepthMask(GL.GL_TRUE)
    GL.glDisable(GL.GL_BLEND)
    GL.glClearColor(0,0,0,0)

    GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, opaqueFBO)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT|GL.GL_DEPTH_BUFFER_BIT)

    GL.glUseProgram(Assets.OPAQUE_SHADER)

    matrix = GL.glGetUniformLocation(Assets.OPAQUE_SHADER, 'mvp')
    GL.glUniformMatrix4fv(matrix, 1, GL.GL_FALSE, np.dot(vp,redModelMat))
    color = GL.glGetUniformLocation(Assets.OPAQUE_SHADER, 'color')
    GL.glUniform3f(color, 1, 0, 0)

    GL.glBindVertexArray(quadVAO)
    GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)

    GL.glDepthMask(GL.GL_FALSE)
    GL.glDepthFunc(GL.GL_ALWAYS)
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunci(0, GL.GL_ONE, GL.GL_ONE)
    GL.glBlendFunci(1, GL.GL_ZERO, GL.GL_ONE_MINUS_SRC_COLOR)
    GL.glBlendEquation(GL.GL_FUNC_ADD)

    GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, transparentFBO)
    GL.glClearBufferfv(GL.GL_COLOR, 0, accumClear)
    GL.glClearBufferfv(GL.GL_COLOR, 1, revealClear)

    GL.glUseProgram(Assets.TRANSPARENT_SHADER)

    projectionMatrix = GL.glGetUniformLocation(Assets.TRANSPARENT_SHADER, 'mvp')
    GL.glUniformMatrix4fv(projectionMatrix, 1, GL.GL_FALSE, np.dot(vp,blueModelMat))
    color = GL.glGetUniformLocation(Assets.TRANSPARENT_SHADER, 'color')
    GL.glUniform4f(color, 0, 0, 1, 0.5)

    GL.glBindVertexArray(quadVAO)
    GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)

    projectionMatrix = GL.glGetUniformLocation(Assets.TRANSPARENT_SHADER, 'mvp')
    GL.glUniformMatrix4fv(projectionMatrix, 1, GL.GL_FALSE, np.dot(vp,greenModelMat))
    color = GL.glGetUniformLocation(Assets.TRANSPARENT_SHADER, 'color')
    GL.glUniform4f(color, 0, 1, 0, 0.5)

    GL.glBindVertexArray(quadVAO)
    GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)

    GL.glDepthFunc(GL.GL_ALWAYS)
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

    GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, opaqueFBO)

    GL.glUseProgram(Assets.COMPOSITE_SHADER)

    GL.glActiveTexture(GL.GL_TEXTURE0)
    GL.glBindTexture(GL.GL_TEXTURE_2D, accumTexture)
    GL.glUniform1i(GL.glGetUniformLocation(Assets.COMPOSITE_SHADER, "accum"), 0)
    GL.glActiveTexture(GL.GL_TEXTURE1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, revealTexture)
    GL.glUniform1i(GL.glGetUniformLocation(Assets.COMPOSITE_SHADER, "reveal"), 1)
    GL.glBindVertexArray(quadVAO)
    GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)
    
    GL.glDisable(GL.GL_DEPTH_TEST)
    GL.glDepthMask(GL.GL_TRUE)
    GL.glDisable(GL.GL_BLEND)
    
    GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
    GL.glClearColor(0,0,0,0)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT | GL.GL_STENCIL_BUFFER_BIT)

    GL.glUseProgram(Assets.SCREEN_SHADER)

    GL.glActiveTexture(GL.GL_TEXTURE0)
    GL.glBindTexture(GL.GL_TEXTURE_2D, opaqueTexture)
    GL.glBindVertexArray(quadVAO)
    GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)

    pygame.display.flip()

    delta = (start - end)/1000000000
    timeCounter += delta
    frames += 1
    if timeCounter >= 1:
        print(f'frame time: {1000000/frames:.0f}us | FPS: {frames}')
        timeCounter -= 1
        frames = 0










