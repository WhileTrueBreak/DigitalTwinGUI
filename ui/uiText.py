from ui.uiElement import GlElement
from constraintManager import *

from asset import *

class UiText(GlElement):
    def __init__(self, window, constraints, dim=(0,0,0,0)):
        constraints.append(ABSOLUTE(T_W, 0))
        constraints.append(ABSOLUTE(T_H, 0))
        super().__init__(window, constraints, dim)
        self.type = 'text'
        
        self.dirtyText = True
        self.font = Assets.FIRACODE_FONT
        self.text = 'default'
        self.fontSize = 48
        self.textSpacing = 5
        self.textColor = (1,1,1)

        self.maxDescender = 0
        self.maxAscender = 0

        self.textIndices = np.array([1,0,3,3,1,2], dtype='int32')
        
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        
        self.textVao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.textVao)

        self.textVbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.textVbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, 4 * 4 * 4, None, GL.GL_DYNAMIC_DRAW)

        GL.glVertexAttribPointer(0, 4, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
        GL.glEnableVertexAttribArray(0)
        
        self.textEbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.textEbo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.textIndices, GL.GL_DYNAMIC_DRAW)

        # unbind vao vbo ebo
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)
    
    def reshape(self):
        return

    def absUpdate(self, delta):
        self.updateTextBound()
        return
    
    def updateTextBound(self):
        if not self.dirtyText:
            return
        scale = self.fontSize/48
        
        maxdes = 0
        maxasc = 0
        x = self.dim[0]
        xStart = x
        y = self.dim[1]
        for c in self.text:
            ch = self.font[c]
            w, h = ch.textureSize
            maxdes = max(maxdes, ch.descender*scale)
            maxasc = max(maxasc, ch.ascender*scale)

            x += w*scale + self.textSpacing*scale
        x -= self.textSpacing*scale
        widthAspect = (x-xStart)/(maxasc+maxdes)
        
        self.maxAscender = maxasc
        self.maxDescender = maxdes

        # find width constraint
        widthConstraint = None
        heightConstraint = None
        for c in self.constraints:
            if c.toChange == T_W:
                widthConstraint = c
            if c.toChange == T_H:
                heightConstraint = c
        
        self.constraints.remove(widthConstraint)
        self.constraints.remove(heightConstraint)
        self.constraints.append(RELATIVE(T_W, widthAspect, T_H))
        self.constraints.append(ABSOLUTE(T_H, self.maxDescender + self.maxAscender))
        self.setDirty()
        self.dirtyText = False

    def absRender(self):
        self.renderText(self.text, Assets.FIRACODE_FONT, self.fontSize/48)
        return
    
    def renderText(self, text, font, scale):
        GL.glUseProgram(Assets.TEXT_SHADER)

        GL.glBindVertexArray(self.textVao)

        GL.glUniform3f(GL.glGetUniformLocation(Assets.TEXT_SHADER, "textColor"), *self.textColor)

        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        x = self.dim[0]
        y = self.dim[1]
        for c in text:
            ch = font[c]
            w, h = ch.textureSize
            w = w*scale
            h = h*scale
            des = ch.descender*scale

            vertices = self.getVertexData(x, y + des + self.maxAscender, w, h)

            #render glyph texture over quad
            GL.glBindTexture(GL.GL_TEXTURE_2D, ch.texture)
            #update content of VBO memory
            
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.textVbo)
            GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

            #render quad
            GL.glBindVertexArray(self.textVao)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.textVbo)
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.textEbo)
            GL.glEnableVertexAttribArray(0)
            GL.glDrawElements(GL.GL_TRIANGLES, len(self.textIndices), GL.GL_UNSIGNED_INT, None)
            GL.glDisableVertexAttribArray(0)
            #now advance cursors for next glyph (note that advance is number of 1/64 pixels)
            x += w*scale + self.textSpacing*scale

        GL.glBindVertexArray(0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def getVertexData(self, xpos, ypos, w, h):
        xpos = (2*xpos)/self.window.dim[0] - 1
        ypos = (2*(self.window.dim[1]-ypos))/self.window.dim[1] - 1
        w = (2*w)/self.window.dim[0]
        h = (2*h)/self.window.dim[1]
        return np.array([
            xpos,       ypos + h, 0, 0,
            xpos,       ypos,     0, 1,
            xpos + w,   ypos,     1, 1,
            xpos + w,   ypos + h, 1, 0
        ], np.float32)
    
    def setText(self, text):
        self.text = text
        self.dirtyText = True
    
    def setFont(self, font):
        self.font = font
        self.dirtyText = True
    
    def setFontSize(self, size):
        self.fontSize = size
        self.dirtyText = True
    
    def setTextSpacing(self, spacing):
        self.textSpacing = spacing
        self.dirtyText = True

    def setTextColor(self, color):
        self.textColor = color
