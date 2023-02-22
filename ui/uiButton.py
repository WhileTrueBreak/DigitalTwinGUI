from ui.uiElement import GlElement

from asset import *

import ctypes

class UiButton(GlElement):
    def __init__(self, window, constraints, dim=(0,0,0,0)):
        super().__init__(window, constraints, dim)
        self.type = 'button'

        self.shader = Assets.SOLID_SHADER
        self.currentColor = (1, 1, 1)
        self.defaultColor = (1, 1, 1)
        self.hoverColor = (1, 1, 1)
        self.pressColor = (1, 1, 1)

        self.lockFlag = False

        self.vertices = np.array([
            [self.openGLDim[0], self.openGLDim[1], *self.currentColor],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1], *self.currentColor],
            [self.openGLDim[0], self.openGLDim[1]+self.openGLDim[3], *self.currentColor],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1]+self.openGLDim[3], *self.currentColor]
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

    def reshape(self):
        self.vertices = np.array([
            [self.openGLDim[0], self.openGLDim[1], *self.currentColor],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1], *self.currentColor],
            [self.openGLDim[0], self.openGLDim[1]+self.openGLDim[3], *self.currentColor],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1]+self.openGLDim[3], *self.currentColor]
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
        return

    def setColor(self, color):
        self.currentColor = color
        self.reshape()
        return

    def setDefaultColor(self, color):
        self.defaultColor = color

    def setHoverColor(self, color):
        self.hoverColor = color

    def setPressColor(self, color):
        self.pressColor = color

    def onDefault(self, callback=None):
        if self.lockFlag: return
        self.setColor(self.defaultColor)
    
    def onHover(self, callback=None):
        if self.lockFlag: return
        self.setColor(self.hoverColor)
    
    def onHeld(self, callback=None):
        if self.lockFlag: return
        self.setColor(self.pressColor)

    def onPress(self, callback=None):
        if self.lockFlag: return
        self.window.uiEvents.append({'obj':self, 'action':'press', 'type':self.type, 'time':time.time_ns()})
    
    def onRelease(self, callback=None):
        if self.lockFlag: return
        self.window.uiEvents.append({'obj':self, 'action':'release', 'type':self.type, 'time':time.time_ns()})

    def lock(self):
        self.lockFlag = True
        self.setColor(self.defaultColor)
        
    def unlock(self):
        self.lockFlag = False
        