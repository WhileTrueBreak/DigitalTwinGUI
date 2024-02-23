from PIL import Image

from connections.mjpegThread import *
from utils.interfaces.pollController import PollController
from asset import *

class MJPEGStream(PollController):
    def __init__(self, url):

        self.url = url
        self.container = StreamContainer()
        self.threadStopFlag = True
        self.thread = None
        # self.thread = createMjpegThread(self.container, self.url, lambda:self.threadStopFlag)
        self.image = None

        self.texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)

        #texture options
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

    @timing
    def update(self, delta):
        stream = self.container.getStream()
        if stream == None: 
            return
        image = Image.open(stream).convert("RGBA")
        stream.close()
        
        wasEmpty = self.image == None
        self.image = image.transpose(Image.FLIP_TOP_BOTTOM).tobytes()
        
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)

        if wasEmpty:
            GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA8, image.width, image.height, 
                            0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, self.image)
        else:
            GL.glTexSubImage2D(GL.GL_TEXTURE_2D, 0, 0, 0, image.width, image.height, 
                            GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, self.image)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
    
    def start(self):
        self.threadStopFlag = False
        if self.thread != None and self.thread.is_alive(): return
        self.thread = createMjpegThread(self.container, self.url, lambda:self.threadStopFlag)

    def stop(self):
        self.threadStopFlag = True
