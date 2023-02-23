import cv2
from PIL import Image

from ui.uiElement import GlElement

import OpenGL.GL as GL
import numpy as np
from asset import *

class UiVideo(GlElement):
    def __init__(self, window, constraints, dim=(0,0,0,0)):
        super().__init__(window, constraints, dim)
        self.type = 'image'

        self.vwidth = 0
        self.vheight = 0

        self.video = None
        self.spf = 1
        self.frameTimer = 0

        self.vertices = np.array([
            [self.openGLDim[0], self.openGLDim[1], 0, 0],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1], 1, 0],
            [self.openGLDim[0], self.openGLDim[1]+self.openGLDim[3], 0, 1],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1]+self.openGLDim[3], 1, 1]
        ], dtype='float32')
        
        self.indices = np.array([1, 0, 3, 3, 0, 2], dtype='int32')

        self.texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)

        self.vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, 4 * 4 * 4, None, GL.GL_DYNAMIC_DRAW)

        GL.glVertexAttribPointer(0, 4, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
        GL.glEnableVertexAttribArray(0)
        
        self.ebo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.indices, GL.GL_DYNAMIC_DRAW)

        # unbind vao vbo ebo
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def reshape(self):
        self.vertices = np.array([
            [self.openGLDim[0], self.openGLDim[1], 0, 0],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1], 1, 0],
            [self.openGLDim[0], self.openGLDim[1]+self.openGLDim[3], 0, 1],
            [self.openGLDim[0]+self.openGLDim[2], self.openGLDim[1]+self.openGLDim[3], 1, 1]
        ], dtype='float32')

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, self.vertices.nbytes, self.vertices)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        return

    def absUpdate(self, delta):
        self.frameTimer += delta
        if self.frameTimer >= self.spf:
            self.frameTimer -= self.spf
            self.__setNextFrame()
        return

    def __setNextFrame(self):
        if self.video == None:
            return
        success, frame = self.video.read()
        if not success:
            cv2.cvSetCaptureProperty(self.video, cv2.CV_CAP_PROP_POS_MSEC, 0)
            success, frame = self.video.read()
        if not success:
            return
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        imgbyte = image.transpose(Image.FLIP_TOP_BOTTOM).tobytes()

        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)

        #texture options
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

        GL.glTexImage2D(GL.GL_TEXTURE_2D,0,GL.GL_RGBA8,image.width,image.height,0,GL.GL_RGB,GL.GL_UNSIGNED_BYTE,imgbyte)
        GL.glGenerateMipmap(GL.GL_TEXTURE_2D)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def absRender(self):
        GL.glUseProgram(Assets.IMAGE_SHADER)

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)

        #render quad
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)

        GL.glEnableVertexAttribArray(0)
        GL.glDrawElements(GL.GL_TRIANGLES, len(self.indices), GL.GL_UNSIGNED_INT, None)
        GL.glDisableVertexAttribArray(0)
        return
    
    def setVideo(self, video):
        self.vwidth = video.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.vheight = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.frameTimer = 0
        self.spf = 1/video.get(cv2.CAP_PROP_FPS)
        self.video = video

    def restartVideo(self):
        cv2.cvSetCaptureProperty(self.video, cv2.CV_CAP_PROP_POS_MSEC, 0)