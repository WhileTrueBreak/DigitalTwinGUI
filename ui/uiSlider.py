from ui.uiElement import GlElement

from asset import *

import ctypes

class UiSlider(GlElement):
    def __init__(self, window, constraints, dim=(0,0,0,0)):
        super().__init__(window, constraints, dim)
        self.type = 'button'

        self.shader = Assets.SOLID_SHADER
        self.baseColor = (1, 1, 1)
        self.sliderColor = (1, 1, 1)

        self.lowerMap = 0
        self.upperMap = 1

        self.currentLoc = 0.5
        self.sliderWidth = 0.05

        self.vertices = np.zeros((12, 5), dtype='float32')
        self.indices = np.array([1, 0, 3, 3, 0, 2, 5, 4, 7, 7, 4, 6, 9, 8, 11, 11, 8, 10], dtype='int32')

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

    def reshape(self):
        self.vertices = self.__genVertices()
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
        return

    def setBaseColor(self, color):
        self.baseColor = color
        self.reshape()
        return

    def setSliderColor(self, color):
        self.sliderColor = color
        self.reshape()
        return
    
    def setSliderPercentage(self, width):
        self.sliderWidth = width

    def setRange(self, lower, upper):
        self.lowerMap = lower
        self.upperMap = upper

    def getValue(self):
        diff = self.upperMap - self.lowerMap
        return self.currentLoc * diff + self.lowerMap

    def setValue(self, value):
        diff = self.upperMap - self.lowerMap
        newV = (value - self.lowerMap)/diff
        if self.currentLoc == newV: return
        self.currentLoc = newV
        self.reshape()

    def onHeld(self, callback=None):
        sliderWidth = self.dim[2]*self.sliderWidth
        sliderrange = self.dim[2]-sliderWidth

        start = self.window.mousePos[0] - self.dim[0] - sliderWidth/2
        self.currentLoc = start/sliderrange
        self.currentLoc = max(0, min(1, self.currentLoc))
        self.reshape()

    def __genVertices(self):
        vertices = np.zeros((12, 5), dtype='float32')
        sliderw = self.openGLDim[2]*self.sliderWidth
        sliderrange = self.openGLDim[2]-sliderw
        leftw = sliderrange*self.currentLoc
        sliderx = self.openGLDim[0]+leftw
        rightw = sliderrange*(1-self.currentLoc)#+sliderw
        rigthx = sliderx+sliderw

        vertices[0] = [self.openGLDim[0], self.openGLDim[1], *self.baseColor]
        vertices[1] = [self.openGLDim[0]+leftw, self.openGLDim[1], *self.baseColor]
        vertices[2] = [self.openGLDim[0], self.openGLDim[1]+self.openGLDim[3], *self.baseColor]
        vertices[3] = [self.openGLDim[0]+leftw, self.openGLDim[1]+self.openGLDim[3], *self.baseColor]

        vertices[4] = [rigthx, self.openGLDim[1], *self.baseColor]
        vertices[5] = [rigthx+rightw, self.openGLDim[1], *self.baseColor]
        vertices[6] = [rigthx, self.openGLDim[1]+self.openGLDim[3], *self.baseColor]
        vertices[7] = [rigthx+rightw, self.openGLDim[1]+self.openGLDim[3], *self.baseColor]

        vertices[8] = [sliderx, self.openGLDim[1], *self.sliderColor]
        vertices[9] = [sliderx+sliderw, self.openGLDim[1], *self.sliderColor]
        vertices[10] = [sliderx, self.openGLDim[1]+self.openGLDim[3], *self.sliderColor]
        vertices[11] = [sliderx+sliderw, self.openGLDim[1]+self.openGLDim[3], *self.sliderColor]

        return vertices

