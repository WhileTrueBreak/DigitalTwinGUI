import OpenGL.GL as GL
import numpy as np
import ctypes
import time

class BatchRenderer:
    MAX_TRANSFORMS = 30
    MAX_VERTICES = 1000000
    def __init__(self, shader, isTransparent=False):
        self.shader = shader
        self.vertices = np.zeros((BatchRenderer.MAX_VERTICES, 11), dtype='float32')
        self.indices = np.zeros(BatchRenderer.MAX_VERTICES, dtype='int32')

        self.isTransparent = isTransparent
        self.transformationMatrices = np.array([np.identity(4)]*BatchRenderer.MAX_TRANSFORMS, dtype='float32')
        self.modelTransformIndex = {}
        self.matrixIndex = 0

        self.modelRange = {}
        self.models = []
        self.currentIndex = 0

        self.isDirty = False
        self.initGLContext()

    def initGLContext(self):
        vertexSize = self.vertices.nbytes

        self.projectionMatrix = GL.glGetUniformLocation(self.shader, 'projectionMatrix')
        self.viewMatrix = GL.glGetUniformLocation(self.shader, 'viewMatrix')

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

        if self.matrixIndex >= BatchRenderer.MAX_TRANSFORMS:
            return -1
        if self.currentIndex + len(model.vertices) > BatchRenderer.MAX_VERTICES:
            return -1
        
        self.transformationMatrices[self.matrixIndex] = transformationMatrix
        matrixIndex = self.matrixIndex
        self.modelTransformIndex[model] = matrixIndex
        self.matrixIndex += 1

        self.models.append(model)
        self.modelRange[model] = (self.currentIndex, self.currentIndex + len(model.vertices))

        vShape = model.vertices.shape
        self.vertices[self.currentIndex:self.currentIndex+vShape[0], 0:6] = model.vertices
        data = np.tile([1, 1, 1, 1, matrixIndex], (vShape[0], 1))
        self.vertices[self.currentIndex:self.currentIndex+vShape[0], 6:11] = data
        indices = np.arange(self.currentIndex, self.currentIndex+vShape[0])
        self.indices[self.currentIndex:self.currentIndex+vShape[0]] = indices

        self.currentIndex += vShape[0]
        self.isDirty = True

        return len(self.models) - 1

    def updateContext(self):
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, self.vertices.nbytes, self.vertices)

        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferSubData(GL.GL_ELEMENT_ARRAY_BUFFER, 0, self.indices.nbytes, self.indices)

        GL.glBindBuffer(GL.GL_SHADER_STORAGE_BUFFER, self.ssbo)
        GL.glBufferSubData(GL.GL_SHADER_STORAGE_BUFFER, 0, self.transformationMatrices.nbytes, self.transformationMatrices)
        GL.glBindBufferBase(GL.GL_SHADER_STORAGE_BUFFER, 0, self.ssbo);

        GL.glBindBuffer(GL.GL_SHADER_STORAGE_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)
        self.isDirty = False

    def render(self):

        if self.isDirty:
            self.updateContext()

        GL.glUseProgram(self.shader)
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

    def setProjectionMatrix(self, matrix):
        GL.glUseProgram(self.shader)
        GL.glUniformMatrix4fv(self.projectionMatrix, 1, GL.GL_FALSE, matrix)
        
    def setViewMatrix(self, matrix):
        GL.glUseProgram(self.shader)
        GL.glUniformMatrix4fv(self.viewMatrix, 1, GL.GL_TRUE, matrix)
    
    def setTransformMatrix(self, id, matrix):
        self.transformationMatrices[id] = matrix.T 
        GL.glBindBuffer(GL.GL_SHADER_STORAGE_BUFFER, self.ssbo)
        GL.glBufferSubData(GL.GL_SHADER_STORAGE_BUFFER, 0, self.transformationMatrices.nbytes, self.transformationMatrices)
        GL.glBindBufferBase(GL.GL_SHADER_STORAGE_BUFFER, 0, self.ssbo)
    
    def setColor(self, id, color):
        model = self.models[id]
        colorMat = np.tile(color, (self.modelRange[model][1]-self.modelRange[model][0], 1))
        self.vertices[self.modelRange[model][0]:self.modelRange[model][1], 6:10] = colorMat
        self.isDirty = True

class Renderer:
    def __init__(self, shader):
        self.shader = shader

        self.projectionMatrix = np.identity(4)
        self.viewMatrix = np.identity(4)
        self.batches = []
        self.addBatch()
    
    def addModel(self, model, matrix):
        for i in range(len(self.batches)):
            id = self.batches[i].addModel(model, matrix)
            if id != -1:
                return (i, id)
        self.addBatch()
        id = self.batches[-1].addModel(model, matrix)
        if id == -1:
            return (-1, -1)
        return (len(self.batches) - 1, id)
    
    def addBatch(self):
        self.batches.append(BatchRenderer(self.shader))
        self.batches[-1].setProjectionMatrix(self.projectionMatrix)
        self.batches[-1].setViewMatrix(self.viewMatrix)

    def setProjectionMatrix(self, matrix):
        self.projectionMatrix = matrix
        for batch in self.batches:
            batch.setProjectionMatrix(matrix)
        
    def setViewMatrix(self, matrix):
        self.viewMatrix = matrix
        for batch in self.batches:
            batch.setViewMatrix(matrix)
    
    def setTransformMatrix(self, id, matrix):
        self.batches[id[0]].setTransformMatrix(id[1], matrix)

    def setColor(self, id, color):
        self.batches[id[0]].setColor(id[1], color)

    def render(self):
        for batch in self.batches:
            batch.render()


