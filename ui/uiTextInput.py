from ui.uiElement import GlElement
from ui.uiText import UiText
from constraintManager import *
import OpenGL.GL as GL
import ctypes
import pygame

from asset import *

eventKeyMapping = {
    ' ':pygame.K_SPACE,
    'a':pygame.K_a,
    'b':pygame.K_b,
    'c':pygame.K_c,
    'd':pygame.K_d,
    'e':pygame.K_e,
    'f':pygame.K_f,
    'g':pygame.K_g,
    'h':pygame.K_h,
    'i':pygame.K_i,
    'j':pygame.K_j,
    'k':pygame.K_k,
    'l':pygame.K_l,
    'm':pygame.K_m,
    'n':pygame.K_n,
    'o':pygame.K_o,
    'p':pygame.K_p,
    'q':pygame.K_q,
    'r':pygame.K_r,
    's':pygame.K_s,
    't':pygame.K_t,
    'u':pygame.K_u,
    'v':pygame.K_v,
    'w':pygame.K_w,
    'x':pygame.K_x,
    'y':pygame.K_y,
    'z':pygame.K_z,
    '0':pygame.K_0,
    '1':pygame.K_1,
    '2':pygame.K_2,
    '3':pygame.K_3,
    '4':pygame.K_4,
    '5':pygame.K_5,
    '6':pygame.K_6,
    '7':pygame.K_7,
    '8':pygame.K_8,
    '9':pygame.K_9,
    '`':pygame.K_BACKQUOTE,
    '-':pygame.K_MINUS,
    '=':pygame.K_EQUALS,
    '[':pygame.K_LEFTBRACKET,
    ']':pygame.K_RIGHTBRACKET,
    '\\':pygame.K_BACKSLASH,
    ';':pygame.K_SEMICOLON,
    '\'':pygame.K_QUOTE,
    ',':pygame.K_COMMA,
    '.':pygame.K_PERIOD,
    '/':pygame.K_SLASH,
}

class UiTextInput(GlElement):
    def __init__(self, window, constraints, dim=(0,0,0,0)):
        super().__init__(window, constraints, dim)
        self.type = 'textinput'
        
        self.dirtyText = True
        self.font = Assets.FIRACODE_FONT
        self.text = ''
        self.fontSize = 48
        self.textSpacing = 10
        self.textColor = (1,1,1)

        self.boxBorderWidth = 2
        self.borderColor = (0,0,0)

        self.maxDescender = 0
        self.maxAscender = 0

        self.initBoxContext()

        constraints = [
            COMPOUND(RELATIVE(T_X, -0.5, T_W), RELATIVE(T_X, 0.5, P_W)),
            COMPOUND(RELATIVE(T_Y, -0.5, T_H), RELATIVE(T_Y, 0.5, P_H))
        ]
        self.textElement = UiText(self.window, constraints)
        self.addChild(self.textElement)

        self.letters = ' abcdefghijklmnopqrstuvwxyz'
        self.lowerSymb = '0123456789-=,./[]\;\'`'
        self.upperSymb = ')!@#$%^&*(_+<>?{}|:"~'

        self.holdDelay = 1000000*500
        self.repeatDelay = 1000000*50

        self.lastState = {'back': False}
        self.holdTimer = {'back': False}
        self.holdFlag = {'back': time.time_ns()}
        self.repeatTimer = {'back': time.time_ns()}
        for key in self.letters:
            self.lastState[key] = False
            self.holdFlag[key] = False
            self.holdTimer[key] = time.time_ns()
            self.repeatTimer[key] = time.time_ns()
        for key in self.lowerSymb:
            self.lastState[key] = False
            self.holdFlag[key] = False
            self.holdTimer[key] = time.time_ns()
            self.repeatTimer[key] = time.time_ns()
    
    def initBoxContext(self):
        self.boxIndices = np.array([1,0,3,3,0,2,3,2,5,5,2,4,5,4,7,7,4,6,7,6,1,1,6,0], dtype='int32')
        self.boxVertices = np.array([
            [0,0,0,0,0],
            [0,0,0,0,0],
            [0,0,0,0,0],
            [0,0,0,0,0],
            [0,0,0,0,0],
            [0,0,0,0,0],
            [0,0,0,0,0],
            [0,0,0,0,0],
        ], dtype='float32')

        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        
        self.boxVao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.boxVao)

        self.boxVbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.boxVbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, 8 * 5 * 4, self.boxVertices, GL.GL_DYNAMIC_DRAW)

        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 5*4, ctypes.c_void_p(0*4))
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, 5*4, ctypes.c_void_p(2*4))
        GL.glEnableVertexAttribArray(1)
        
        self.boxEbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.boxEbo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.boxIndices, GL.GL_DYNAMIC_DRAW)

        # unbind vao vbo ebo
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def reshape(self):
        borderW = (self.boxBorderWidth/self.window.dim[0])*2
        borderH = (self.boxBorderWidth/self.window.dim[1])*2
        points = [
            self.openGLDim[0],
            self.openGLDim[1],
            self.openGLDim[0]+self.openGLDim[2],
            self.openGLDim[1]+self.openGLDim[3]
        ]
        self.boxVertices = np.array([
            [points[0],points[1],*self.borderColor],
            [points[0]+borderW,points[1]+borderH,*self.borderColor],
            [points[2],points[1],*self.borderColor],
            [points[2]-borderW,points[1]+borderH,*self.borderColor],
            [points[2],points[3],*self.borderColor],
            [points[2]-borderW,points[3]-borderH,*self.borderColor],
            [points[0],points[3],*self.borderColor],
            [points[0]+borderW,points[3]-borderH,*self.borderColor],
        ], dtype='float32')
        print(borderW, borderH)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.boxVbo)
        GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, self.boxVertices.nbytes, self.boxVertices)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        return

    def absUpdate(self, delta):
        if self.window.selectedUi == self.text:
            self.window.selectedUi = self
        self.updateText()
        return

    def updateText(self):
        if self.window.selectedUi != self and self.window.selectedUi != self.textElement:
            return
        mods = pygame.key.get_mods()
        shift = mods & pygame.KMOD_SHIFT > 0
        caps = (mods & pygame.KMOD_CAPS > 0) ^ shift
        buffer = ''

        for letter in self.letters:
            # check if pressed
            #   press key
            #   start hold timer
            # check if hold timer is past delay
            #   press key
            #   start repeat timer
            # check if repeat timer is past delay
            #   press key
            #   restart repeat timer

            keyState = self.window.getKeyState(eventKeyMapping[letter])
            if not keyState:
                self.lastState[letter] = False
                self.holdFlag[letter] = False
                continue
            if not self.lastState[letter] and keyState:
                self.lastState[letter] = True
                self.holdTimer[letter] = time.time_ns()
                if caps: letter = letter.upper()
                buffer += letter
                continue
            if time.time_ns() >= self.holdTimer[letter]+self.holdDelay and not self.holdFlag[letter]:
                self.holdFlag[letter] = True
                self.repeatTimer[letter] = time.time_ns()
                if caps: letter = letter.upper()
                buffer += letter
                continue
            if time.time_ns() >= self.repeatTimer[letter]+self.repeatDelay and self.holdFlag[letter]:
                self.repeatTimer[letter] = time.time_ns()
                if caps: letter = letter.upper()
                buffer += letter
                continue
        
        for i in range(len(self.lowerSymb)):
            keyState = self.window.getKeyState(eventKeyMapping[self.lowerSymb[i]])
            if not keyState:
                self.lastState[self.lowerSymb[i]] = False
                self.holdFlag[self.lowerSymb[i]] = False
                continue
            if not self.lastState[self.lowerSymb[i]] and keyState:
                self.lastState[self.lowerSymb[i]] = True
                self.holdTimer[self.lowerSymb[i]] = time.time_ns()
                letter = self.lowerSymb[i]
                if shift: letter = self.upperSymb[i]
                buffer += letter
                continue
            if time.time_ns() >= self.holdTimer[self.lowerSymb[i]]+self.holdDelay and not self.holdFlag[self.lowerSymb[i]]:
                self.holdFlag[self.lowerSymb[i]] = True
                self.repeatTimer[self.lowerSymb[i]] = time.time_ns()
                letter = self.lowerSymb[i]
                if shift: letter = self.upperSymb[i]
                buffer += letter
                continue
            if time.time_ns() >= self.repeatTimer[self.lowerSymb[i]]+self.repeatDelay and self.holdFlag[self.lowerSymb[i]]:
                self.repeatTimer[self.lowerSymb[i]] = time.time_ns()
                letter = self.lowerSymb[i]
                if shift: letter = self.upperSymb[i]
                buffer += letter
                continue

        if buffer != '':
            self.text += buffer
            self.textElement.setText(self.text)
        
        keyState = self.window.getKeyState(pygame.K_BACKSPACE)
        if not keyState:
            self.lastState['back'] = False
            self.holdFlag['back'] = False
            return
        if not self.lastState['back'] and keyState:
            self.lastState['back'] = True
            self.holdTimer['back'] = time.time_ns()
            self.text = self.text[:-1]
            self.textElement.setText(self.text)
            return
        if time.time_ns() >= self.holdTimer['back']+self.holdDelay and not self.holdFlag['back']:
            self.holdFlag['back'] = True
            self.repeatTimer['back'] = time.time_ns()
            self.text = self.text[:-1]
            self.textElement.setText(self.text)
            return
        if time.time_ns() >= self.repeatTimer['back']+self.repeatDelay and self.holdFlag['back']:
            self.repeatTimer['back'] = time.time_ns()
            self.text = self.text[:-1]
            self.textElement.setText(self.text)
            return

    def absRender(self):
        self.renderTextBox()
        return
    
    def renderTextBox(self):
        GL.glUseProgram(Assets.SOLID_SHADER)
        GL.glBindVertexArray(self.boxVao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.boxVbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.boxEbo)

        GL.glEnableVertexAttribArray(0)
        GL.glEnableVertexAttribArray(1)

        GL.glDrawElements(GL.GL_TRIANGLES, len(self.boxIndices), GL.GL_UNSIGNED_INT, None)

        GL.glDisableVertexAttribArray(1)
        GL.glDisableVertexAttribArray(0)
    
    def getText(self):
        return self.text

    def setFont(self, font):
        self.textElement.setFont(font)
    
    def setFontSize(self, size):
        self.textElement.setFontSize(size)
    
    def setTextSpacing(self, spacing):
        self.textElement.setTextSpacing(spacing)

    def setTextColor(self, color):
        self.textElement.setTextColor(color)

    def setBorderColor(self, color):
        self.borderColor = color
        self.isDirty = True
    
    def setBorderWeight(self, weight):
        self.boxBorderWidth = weight
        self.isDirty = True