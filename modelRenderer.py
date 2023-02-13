from asset import *

import OpenGL.GL as GL
import numpy as np
import ctypes
import time

class BatchRenderer:
    MAX_TRANSFORMS = 9
    MAX_VERTICES = 1000000
    def __init__(self, isTransparent=False):
        self.vertices = np.zeros((BatchRenderer.MAX_VERTICES, 11), dtype='float32')
        self.indices = np.arange(BatchRenderer.MAX_VERTICES, dtype='int32')

        self.isTransparent = isTransparent

        self.isAvaliable = [True]*BatchRenderer.MAX_TRANSFORMS

        self.transformationMatrices = np.array([np.identity(4)]*BatchRenderer.MAX_TRANSFORMS, dtype='float32')
        self.modelRange = np.zeros((BatchRenderer.MAX_TRANSFORMS, 2), dtype='int32')
        self.models = [None]*BatchRenderer.MAX_TRANSFORMS
        
        self.currentIndex = 0

        self.isDirty = False
        self.initGLContext()

    def initGLContext(self):
        vertexSize = self.vertices.nbytes

        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)

        self.vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertices, GL.GL_DYNAMIC_DRAW)

        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 11*4, ctypes.c_void_p(0*4))
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_TRUE, 11*4, ctypes.c_void_p(3*4))
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(2, 4, GL.GL_FLOAT, GL.GL_FALSE, 11*4, ctypes.c_void_p(6*4))
        GL.glEnableVertexAttribArray(2)
        GL.glVertexAttribPointer(3, 1, GL.GL_FLOAT, GL.GL_FALSE, 11*4, ctypes.c_void_p(10*4))
        GL.glEnableVertexAttribArray(3)

        self.ebo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.indices, GL.GL_DYNAMIC_DRAW)

        self.ssbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_SHADER_STORAGE_BUFFER, self.ssbo)
        GL.glBufferData(GL.GL_SHADER_STORAGE_BUFFER, self.transformationMatrices, GL.GL_DYNAMIC_DRAW)
        GL.glBindBufferBase(GL.GL_SHADER_STORAGE_BUFFER, 0, self.ssbo)

        GL.glBindBuffer(GL.GL_SHADER_STORAGE_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def addModel(self, model, transformationMatrix):
        transformationMatrix = transformationMatrix.T
        if not True in self.isAvaliable:
            return -1
        if self.currentIndex + len(model.vertices) > BatchRenderer.MAX_VERTICES:
            return -1

        vShape = model.vertices.shape
        index = self.isAvaliable.index(True)
        self.isAvaliable[index] = False

        self.models[index] = model
        self.transformationMatrices[index] = transformationMatrix
        self.modelRange[index] = [self.currentIndex, self.currentIndex+vShape[0]]

        self.vertices[self.currentIndex:self.currentIndex+vShape[0], 0:6] = model.vertices
        data = np.tile([1, 1, 1, 1, index], (vShape[0], 1))
        self.vertices[self.currentIndex:self.currentIndex+vShape[0], 6:11] = data

        self.currentIndex += vShape[0]
        self.isDirty = True

        return index

    def removeModel(self, id):
        self.isAvaliable[id] = True
        # shift vertices
        lower = self.modelRange[id][0]
        upper = self.modelRange[id][1]
        right = self.vertices[upper::]
        self.vertices[lower:lower+len(right)] = right

        #update all later ranges
        for i in range(len(self.modelRange)):
            if self.modelRange[i][0] < upper: continue
            self.modelRange[i][0] -= upper-lower
            self.modelRange[i][1] -= upper-lower

        self.currentIndex -= upper-lower
        self.isDirty = True
        return

    def updateContext(self):
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, self.vertices.nbytes, self.vertices)

        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferSubData(GL.GL_ELEMENT_ARRAY_BUFFER, 0, self.indices.nbytes, self.indices)

        GL.glBindBuffer(GL.GL_SHADER_STORAGE_BUFFER, self.ssbo)
        GL.glBufferSubData(GL.GL_SHADER_STORAGE_BUFFER, 0, self.transformationMatrices.nbytes, self.transformationMatrices)
        GL.glBindBufferBase(GL.GL_SHADER_STORAGE_BUFFER, 0, self.ssbo)

        GL.glBindBuffer(GL.GL_SHADER_STORAGE_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)
        self.isDirty = False

    def render(self):

        if self.isDirty:
            self.updateContext()

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)

        GL.glBindBuffer(GL.GL_SHADER_STORAGE_BUFFER, self.ssbo)
        GL.glBindBufferBase(GL.GL_SHADER_STORAGE_BUFFER, 0, self.ssbo)

        GL.glEnableVertexAttribArray(0)
        GL.glEnableVertexAttribArray(1)
        GL.glEnableVertexAttribArray(2)
        GL.glEnableVertexAttribArray(3)

        GL.glDrawElements(GL.GL_TRIANGLES, self.currentIndex, GL.GL_UNSIGNED_INT, None)

        GL.glDisableVertexAttribArray(3)
        GL.glDisableVertexAttribArray(2)
        GL.glDisableVertexAttribArray(1)
        GL.glDisableVertexAttribArray(0)

    def setProjectionMatrix(self, shader, matrix):
        GL.glUseProgram(shader)
        projectionMatrix = GL.glGetUniformLocation(shader, 'projectionMatrix')
        GL.glUniformMatrix4fv(projectionMatrix, 1, GL.GL_FALSE, matrix)
        
    def setViewMatrix(self, shader, matrix):
        GL.glUseProgram(shader)
        viewMatrix = GL.glGetUniformLocation(shader, 'viewMatrix')
        GL.glUniformMatrix4fv(viewMatrix, 1, GL.GL_TRUE, matrix)
    
    def setTransformMatrix(self, id, matrix):
        self.transformationMatrices[id] = matrix.T 
        GL.glBindBuffer(GL.GL_SHADER_STORAGE_BUFFER, self.ssbo)
        GL.glBufferSubData(GL.GL_SHADER_STORAGE_BUFFER, 0, self.transformationMatrices.nbytes, self.transformationMatrices)
        GL.glBindBufferBase(GL.GL_SHADER_STORAGE_BUFFER, 0, self.ssbo)
    
    def setColor(self, id, color):
        lower = self.modelRange[id][0]
        upper = self.modelRange[id][1]
        colorMat = np.tile(color, (upper-lower, 1))
        self.vertices[lower:upper, 6:10] = colorMat
        self.isDirty = True

    def getData(self, id):
        return (self.models[id], self.transformationMatrices[id])

class Renderer:
    def __init__(self, window, supportTransparency=False):
        self.window = window
        self.supportTransparency = supportTransparency

        self.opaqueShader = Assets.OPAQUE_SHADER
        self.transparentShader = Assets.TRANSPARENT_SHADER
        self.compositeShader = Assets.COMPOSITE_SHADER
        self.screenShader = Assets.SCREEN_SHADER

        self.idDict = {}
        self.nextId = 0

        self.projectionMatrix = np.identity(4)
        self.viewMatrix = np.identity(4)

        self.transparentBatch = []
        self.solidBatch = []
        self.batches = []

        self.initCompositeLayers()
    
    def initCompositeLayers(self):
        self.quadVertices = np.array([
            [-1,-1,-1, 0, 0],
            [ 1,-1,-1, 1, 0],
            [ 1, 1,-1, 1, 1],
            [ 1, 1,-1, 1, 1],
            [-1, 1,-1, 0, 1],
            [-1,-1,-1, 0, 0],
        ], dtype='float32')
        self.quadVAO = GL.glGenVertexArrays(1)
        self.quadVBO = GL.glGenBuffers(1)
        GL.glBindVertexArray(self.quadVAO)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.quadVBO)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.quadVertices.nbytes, self.quadVertices, GL.GL_DYNAMIC_DRAW)
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 5 * 4, ctypes.c_void_p(0*4))
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 5 * 4, ctypes.c_void_p(3*4))
        GL.glBindVertexArray(0)

        self.opaqueFBO = GL.glGenFramebuffers(1)
        self.transparentFBO = GL.glGenFramebuffers(1)

        self.opaqueTexture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.opaqueTexture)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA16F, self.window.dim[0], self.window.dim[1], 0, GL.GL_RGBA, GL.GL_HALF_FLOAT, None)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

        self.depthTexture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.depthTexture)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_DEPTH_COMPONENT, self.window.dim[0], self.window.dim[1], 0, GL.GL_DEPTH_COMPONENT, GL.GL_FLOAT, None)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.opaqueFBO)
        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, self.opaqueTexture, 0)
        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_DEPTH_ATTACHMENT, GL.GL_TEXTURE_2D, self.depthTexture, 0)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

        self.accumTexture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.accumTexture)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA16F, self.window.dim[0], self.window.dim[1], 0, GL.GL_RGBA, GL.GL_HALF_FLOAT, None)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

        self.revealTexture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.revealTexture)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_R8, self.window.dim[0], self.window.dim[1], 0, GL.GL_RED, GL.GL_FLOAT, None)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.transparentFBO)
        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, self.accumTexture, 0)
        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT1, GL.GL_TEXTURE_2D, self.revealTexture, 0)
        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_DEPTH_ATTACHMENT, GL.GL_TEXTURE_2D, self.depthTexture, 0)

        self.transparentDrawBuffers = (GL.GL_COLOR_ATTACHMENT0, GL.GL_COLOR_ATTACHMENT1)
        GL.glDrawBuffers(self.transparentDrawBuffers)

    def addModel(self, model, matrix):
        for i in range(len(self.batches)):
            id = self.batches[i].addModel(model, matrix)
            if id == -1: continue
            modelId = self.nextId
            self.nextId += 1
            self.idDict[modelId] = (i, id)
            return modelId
        self.addBatch()
        id = self.batches[-1].addModel(model, matrix)
        if id == -1:
            return -1
        modelId = self.nextId
        self.nextId += 1
        self.idDict[modelId] = (len(self.batches) - 1, id)
        return modelId
    
    def removeModel(self, id):
        self.batches[self.idDict[id][0]].removeModel(self.idDict[id][1])
        self.idDict.pop(id)
    
    def addBatch(self, transparent=False):
        print('creating new batch')
        self.batches.append(BatchRenderer(transparent))
        shader = self.opaqueShader
        if transparent:
            shader = self.transparentShader
            self.transparentBatch.append(self.batches[-1])
        else:
            self.solidBatch.append(self.batches[-1])
        self.batches[-1].setProjectionMatrix(shader, self.projectionMatrix)
        self.batches[-1].setViewMatrix(shader, self.viewMatrix)

    def setProjectionMatrix(self, matrix):
        self.projectionMatrix = matrix
        for batch in self.solidBatch:
            batch.setProjectionMatrix(self.opaqueShader, matrix)
        for batch in self.transparentBatch:
            batch.setProjectionMatrix(self.transparentShader, matrix)
        
    def setViewMatrix(self, matrix):
        self.viewMatrix = matrix
        for batch in self.solidBatch:
            batch.setViewMatrix(self.opaqueShader, matrix)
        for batch in self.transparentBatch:
            batch.setViewMatrix(self.transparentShader, matrix)
    
    def setTransformMatrix(self, id, matrix):
        self.batches[self.idDict[id][0]].setTransformMatrix(self.idDict[id][1], matrix)

    def setColor(self, id, color):
        batch = self.batches[self.idDict[id][0]]
        objId = self.idDict[id][1]
        isTransparent = color[3] != 1

        #is trans or solid
        if not (isTransparent ^ batch.isTransparent):
            batch.setColor(objId, color)
            return

        # remove from batch and added to new batch
        model, matrix = batch.getData(objId)
        batch.removeModel(objId)

        #loop through batches
        for i in range(len(self.batches)):
            if isTransparent ^ self.batches[i].isTransparent: continue
            objId = self.batches[i].addModel(model, matrix)
            if objId == -1: continue
            self.batches[i].setColor(objId, color)
            self.idDict[id] = (i, objId)
            return

        #if didnt find suitable batch
        self.addBatch(isTransparent)
        batchId = len(self.batches)-1
        objId = self.batches[-1].addModel(model, matrix)
        if objId == -1:
            print('failed to update color')
            return
        self.batches[batchId].setColor(objId, color)
        self.idDict[id] = (batchId, objId)

    def render(self):
        # config states
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LESS)
        GL.glDepthMask(GL.GL_TRUE)
        GL.glDisable(GL.GL_BLEND)
        GL.glClearColor(0,0,0,0)

        # render opaque
        GL.glUseProgram(self.opaqueShader)
        for batch in self.solidBatch:
            batch.render()

        # config states
        GL.glDepthMask(GL.GL_FALSE)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunci(0, GL.GL_ONE, GL.GL_ONE)
        GL.glBlendFunci(1, GL.GL_ZERO, GL.GL_ONE_MINUS_SRC_COLOR)
        GL.glBlendEquation(GL.GL_FUNC_ADD)

        # render transparent
        GL.glUseProgram(self.transparentShader)
        for batch in self.transparentBatch:
            batch.render()

        # config states
        GL.glDepthFunc(GL.GL_ALWAYS)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        # render composite
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.opaqueFBO)

        GL.glUseProgram(self.compositeShader)

        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.accumTexture)
        GL.glUniform1i(GL.glGetUniformLocation(Assets.COMPOSITE_SHADER, "accum"), 0)
        GL.glActiveTexture(GL.GL_TEXTURE1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.revealTexture)
        GL.glUniform1i(GL.glGetUniformLocation(Assets.COMPOSITE_SHADER, "reveal"), 1)
        GL.glBindVertexArray(self.quadVAO)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)

        # config states
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glDepthMask(GL.GL_TRUE)
        GL.glDisable(GL.GL_BLEND)

        # render to screen
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
        GL.glClearColor(0,0,0,0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT | GL.GL_STENCIL_BUFFER_BIT)

        GL.glUseProgram(self.screenShader)

        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.opaqueTexture)
        GL.glBindVertexArray(self.quadVAO)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)

        # reset states
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glDepthFunc(GL.GL_LESS)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_BLEND)
        GL.glCullFace(GL.GL_BACK)
        GL.glClearColor(0, 0, 0, 1)


