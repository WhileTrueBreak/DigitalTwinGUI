from ui.uiElement import GlElement

from PIL import Image

from connections.mjpegThread import *
from asset import *

class UiStream(GlElement):
    def __init__(self, window, constraints, url, dim=(0,0,0,0)):
        super().__init__(window, constraints, dim)
        self.type = 'stream'

        self.url = url
        self.container = StreamContainer()
        self.threadStopFlag = True
        self.thread = createMjpegThread(self.container, self.url, lambda:self.threadStopFlag)
        self.image = None

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
        self.updateImage(delta)
        return

    def updateImage(self, delta):
        stream = self.container.getStream()
        if stream == None: 
            return
        image = Image.open(stream).convert("RGBA")
        stream.close()
        self.image = image.transpose(Image.FLIP_TOP_BOTTOM).tobytes()
        
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)

        #texture options
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

        GL.glTexImage2D(
                GL.GL_TEXTURE_2D,    # where to load texture data
                0,                # mipmap level
                GL.GL_RGBA8,         # format to store data in
                image.width,                # image dimensions
                image.height,                #
                0,                # border thickness
                GL.GL_RGBA,          # format data is provided in
                GL.GL_UNSIGNED_BYTE, # type to read data as
                self.image)       # data to load as texture
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
    
    def start(self):
        self.threadStopFlag = False
        if self.thread.is_alive(): return
        self.thread = createMjpegThread(self.container, self.url, lambda:self.threadStopFlag)

    def stop(self):
        self.threadStopFlag = True
