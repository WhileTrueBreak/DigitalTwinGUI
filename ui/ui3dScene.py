from ui.uiElement import GlElement

from modelRenderer import *
from mathHelper import *
from asset import *

class Ui3DScene(GlElement):
    def __init__(self, window, constraints, supportTransparency=False, dim=(0,0,0,0)):
        super().__init__(window, constraints, dim)

        self.NEAR_PLANE = 0.01
        self.FAR_PLANE = 1000
        self.FOV = 80

        self.shader = Assets.SOLID_SHADER
        self.color = (1, 1, 1)
        self.vertices = np.array([
            [self.openGLDim[0], self.openGLDim[1], *self.color],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1], *self.color],
            [self.openGLDim[0], self.openGLDim[1]+self.openGLDim[3], *self.color],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1]+self.openGLDim[3], *self.color]
        ], dtype='float32')
        self.indices = np.array([1, 0, 3, 3, 0, 2], dtype='int32')

        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)

        self.vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertices, GL.GL_DYNAMIC_DRAW)

        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 5*4, ctypes.c_void_p(0*4))
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_TRUE, 5*4, ctypes.c_void_p(2*4))
        GL.glEnableVertexAttribArray(1)

        self.ebo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.indices, GL.GL_DYNAMIC_DRAW)

        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        self.modelRenderer = Renderer(self.window, supportTransparency)
        self.modelRenderer.setProjectionMatrix(createProjectionMatrix(self.dim[2], self.dim[3], self.FOV, self.NEAR_PLANE, self.FAR_PLANE))
        self.modelRenderer.setViewMatrix(createViewMatrix(0, 0, 0, 0, 0, 0))
        self.type = '3d scene'

    def reshape(self):
        self.modelRenderer.setProjectionMatrix(createProjectionMatrix(self.dim[2], self.dim[3], self.FOV, self.NEAR_PLANE, self.FAR_PLANE))
        self.modelRenderer.updateCompositeLayers()
        self.vertices = np.array([
            [self.openGLDim[0], self.openGLDim[1], *self.color],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1], *self.color],
            [self.openGLDim[0], self.openGLDim[1]+self.openGLDim[3], *self.color],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1]+self.openGLDim[3], *self.color]
        ], dtype='float32')
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, self.vertices.nbytes, self.vertices)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        return

    def absUpdate(self, delta):
        return

    def absRender(self):
        GL.glUseProgram(self.shader)
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)

        GL.glEnableVertexAttribArray(0)
        GL.glEnableVertexAttribArray(1)

        GL.glDrawElements(GL.GL_TRIANGLES, len(self.indices), GL.GL_UNSIGNED_INT, None)

        GL.glDisableVertexAttribArray(1)
        GL.glDisableVertexAttribArray(0)

        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_DEPTH_TEST)

        GL.glViewport(int(self.dim[0]), int(self.window.dim[1]-self.dim[3]-self.dim[1]), int(self.dim[2]), int(self.dim[3]))
        
        self.modelRenderer.render()

        GL.glViewport(0, 0, *self.window.dim)

        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glDisable(GL.GL_CULL_FACE)
        return

    def setViewMatrix(self, matrix):
        self.modelRenderer.setViewMatrix(matrix)
    
    def getRenderer(self):
        return self.modelRenderer

    def setBackgroundColor(self, color):
        self.color = color
        self.reshape()
        return
