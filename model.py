from OpenGL import GL
from stl import mesh
from asset import *
import numpy as np
import ctypes


class Model:
    def __init__(self, file):
        print(f'Loading Model: {file}')

        self.color = [1,1,1]

        faces = self.loadSTL(file)
        self.vertices, self.indices = self.createVertices(faces)
        self.initVertices(self.vertices, self.indices)
        self.shader = Assets.OBJECT_SHADER
        self.initUniforms(self.shader)
        self.setTransformMatrix(np.identity(4))
        self.setProjectionMatrix(np.identity(4))
        self.setViewMatrix(np.identity(4))

    def loadSTL(self, file):
        try:
            self.mesh = mesh.Mesh.from_file(file)
            faces = np.array(self.mesh.vectors).reshape(len(self.mesh.vectors)*3, 3)
            return faces
        except Exception:
            raise Exception(f'Error loading stl: {file}')
    
    def createVertices(self, faces):
        normals = []
        for face in self.mesh.vectors:
            v1 = np.subtract(face[1], face[0])
            v2 = np.subtract(face[2], face[0])
            normal = self.normalize(np.cross(v1, v2))
            normals.append(normal)
        vertices = []
        for i in range(len(faces)):
            vertices.append([*faces[i], *normals[int(i/3)], *self.color])
        vertices = np.array(vertices, dtype='float32')
        indices = np.array([i for i in range(len(faces))], dtype='int32')
        return (vertices, indices)

    def initVertices(self, vertices, indices):
        vertexSize = vertices[0].nbytes

        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)

        self.vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices, GL.GL_DYNAMIC_DRAW)

        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 9*4, ctypes.c_void_p(0*4))
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_TRUE, 9*4, ctypes.c_void_p(3*4))
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(2, 3, GL.GL_FLOAT, GL.GL_FALSE, 9*4, ctypes.c_void_p(6*4))
        GL.glEnableVertexAttribArray(2)

        self.ebo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, indices, GL.GL_DYNAMIC_DRAW)

        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def initUniforms(self, shader):
        self.transformationMatrix = GL.glGetUniformLocation(shader, 'transformationMatrix')
        self.projectionMatrix = GL.glGetUniformLocation(shader, 'projectionMatrix')
        self.viewMatrix = GL.glGetUniformLocation(shader, 'viewMatrix')

    def setTransformMatrix(self, matrix):
        GL.glUseProgram(self.shader)
        GL.glUniformMatrix4fv(self.transformationMatrix, 1, GL.GL_TRUE, matrix)
    
    def setProjectionMatrix(self, matrix):
        GL.glUseProgram(self.shader)
        GL.glUniformMatrix4fv(self.projectionMatrix, 1, GL.GL_FALSE, matrix)
        
    def setViewMatrix(self, matrix):
        GL.glUseProgram(self.shader)
        GL.glUniformMatrix4fv(self.viewMatrix, 1, GL.GL_TRUE, matrix)
        
    def render(self):
        GL.glUseProgram(self.shader)
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)

        GL.glEnableVertexAttribArray(0)
        GL.glEnableVertexAttribArray(1)
        GL.glEnableVertexAttribArray(2)

        GL.glDrawElements(GL.GL_TRIANGLES, len(self.indices), GL.GL_UNSIGNED_INT, None)

        GL.glDisableVertexAttribArray(2)
        GL.glDisableVertexAttribArray(1)
        GL.glDisableVertexAttribArray(0)

    def normalize(self, v):
        norm = np.linalg.norm(v)
        if norm == 0: 
            return v
        return v / norm

    def setColor(self, color):
        for v in self.vertices:
            v[6] = color[0]
            v[7] = color[1]
            v[8] = color[2]
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, self.vertices.nbytes, self.vertices)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)







