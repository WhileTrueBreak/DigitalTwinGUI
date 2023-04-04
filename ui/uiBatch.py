from asset import Assets

import OpenGL.GL as GL

import numpy as np
import ctypes

class UiBatch:

    POS_SIZE = 2
    POS_OFFSET = 0
    COLOR_SIZE = 4
    COLOR_OFFSET = POS_OFFSET+POS_SIZE
    UV_SIZE = 2
    UV_OFFSET = COLOR_OFFSET+COLOR_SIZE
    TEX_ID_SIZE = 1
    TEX_ID_OFFSET = UV_OFFSET+UV_SIZE

    VERTEX_SIZE = POS_SIZE+COLOR_SIZE+UV_SIZE+TEX_ID_SIZE

    NUM_VERTICES = 4
    NUM_ELEMENTS = 6

    def __init__(self, maxRenderers):
        self.maxRenderers = maxRenderers
        self.maxTextures = 8

        self.numRenderers = 0
        self.uiRenderers = []

        self.vertices = np.zeros((self.maxRenderers*UiBatch.NUM_VERTICES, UiBatch.VERTEX_SIZE), dtype='float32')
        self.indices = self.__genDefaultIndices()
        self.textures = []
        
        self.rebufferData = False
        self.__initVertices()

    def __initVertices(self):

        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)

        self.vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertices, GL.GL_DYNAMIC_DRAW)

        self.ebo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.indices, GL.GL_DYNAMIC_DRAW)

        GL.glVertexAttribPointer(0, UiBatch.POS_SIZE, GL.GL_FLOAT, GL.GL_FALSE, UiBatch.VERTEX_SIZE*4, ctypes.c_void_p(UiBatch.POS_OFFSET*4))
        GL.glVertexAttribPointer(1, UiBatch.COLOR_SIZE, GL.GL_FLOAT, GL.GL_TRUE, UiBatch.VERTEX_SIZE*4, ctypes.c_void_p(UiBatch.COLOR_OFFSET*4))
        GL.glVertexAttribPointer(2, UiBatch.UV_SIZE, GL.GL_FLOAT, GL.GL_TRUE, UiBatch.VERTEX_SIZE*4, ctypes.c_void_p(UiBatch.UV_OFFSET*4))
        GL.glVertexAttribPointer(3, UiBatch.TEX_ID_SIZE, GL.GL_FLOAT, GL.GL_TRUE, UiBatch.VERTEX_SIZE*4, ctypes.c_void_p(UiBatch.TEX_ID_OFFSET*4))

        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)
    
    def render(self):

        for i in range(len(self.uiRenderers)):
            if(self.uiRenderers[i].isDirtyVertex):
                self.__updateVertexData(i)
                self.uiRenderers[i].setCleanVertex()
            rebufferData = True
        if self.rebufferData:
            self.rebuffer()

        GL.glUseProgram(Assets.GUI_SHADER)
        
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)

        for i in range(len(self.textures)):
            GL.glActiveTexture(GL.GL_TEXTURE0 + i)
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.textures[i])

        GL.glEnableVertexAttribArray(0)
        GL.glEnableVertexAttribArray(1)
        GL.glEnableVertexAttribArray(2)
        GL.glEnableVertexAttribArray(3)

        GL.glDrawElements(GL.GL_TRIANGLES, self.numRenderers * UiBatch.NUM_ELEMENTS, GL.GL_UNSIGNED_INT, None)

        GL.glDisableVertexAttribArray(3)
        GL.glDisableVertexAttribArray(2)
        GL.glDisableVertexAttribArray(1)
        GL.glDisableVertexAttribArray(0)

        for i in range(len(self.textures)):
            GL.glActiveTexture(GL.GL_TEXTURE0 + i)
            GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def rebuffer(self):
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, self.vertices)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferSubData(GL.GL_ELEMENT_ARRAY_BUFFER, 0, self.indices)
        
        self.rebufferData = False

    def addRenderer(self, renderer):
        index = self.numRenderers
        self.numRenderers += 1

        self.uiRenderers.append(renderer)
        self.__addtexture(renderer.getTexture())
        self.__updateVertexData(index)
    
    def __addtexture(self, texture):
        if texture == None:
            return
        if texture in self.textures:
            return
        self.textures.append(texture)
    
    def __updateVertexData(self, index):
        renderer = self.uiRenderers[index]
        index = index * UiBatch.NUM_VERTICES
        vertexPos = renderer.getTransform().getVertices()
        for i in range(UiBatch.NUM_VERTICES):
            self.vertices[index][0] = vertexPos[i][0]
            self.vertices[index][1] = vertexPos[i][1]

            self.vertices[index][2] = renderer.getColor()[0]
            self.vertices[index][3] = renderer.getColor()[1]
            self.vertices[index][4] = renderer.getColor()[2]
            self.vertices[index][5] = renderer.getColor()[3]

            self.vertices[index][6] = renderer.getTexCoords()[i][0]
            self.vertices[index][7] = renderer.getTexCoords()[i][1]

            self.vertices[index][8] = -1 if renderer.getTexture() == None else self.textures.index(renderer.getTexture())
            index += 1
        self.rebuffer()
    
    def __genDefaultIndices(self):
        indices = np.zeros((self.maxRenderers, UiBatch.NUM_ELEMENTS), dtype='int32')
        for i in range(self.maxRenderers):
            self.__genElementIndices(indices, i)
        return indices
    
    def __genElementIndices(self, indices, index):
        indOffset = UiBatch.NUM_VERTICES*index
        indices[index][0] = indOffset + 0
        indices[index][1] = indOffset + 1
        indices[index][2] = indOffset + 2
        indices[index][3] = indOffset + 2
        indices[index][4] = indOffset + 3
        indices[index][5] = indOffset + 0

    def hasRoom(self, renderer):
        if len(self.uiRenderers) >= self.maxRenderers:
            return False
        if not renderer.getTexture() in self.textures and \
                len(self.textures) >= self.maxTextures:
            return False
        return True



