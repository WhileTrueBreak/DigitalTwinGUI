import cv2
from PIL import Image
import OpenGL.GL as GL

class VideoPlayer:

    @classmethod
    def fromGif(cls, video, fps):
        ...
    
    @classmethod
    def fromMP4(cls, video):
        ...

    @classmethod
    def fromCapture(cls, cap, fps=None):
        if fps == None:
            fps = cap.get(cv2.CAP_PROP_FPS)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        return cls(cap, fps, width, height)
        

    def __init__(self, capture, fps, width, height):
        self.cap = capture
        self.fps = fps
        self.spf = 1/fps
        self.width = width
        self.height = height

        self.delta = 0

        self.__initTexture()

    
    def __initTexture(self):
        self.texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
    
    def update(self, delta):
        self.delta += delta
        if self.delta >= self.spf:
            self.delta -= self.spf
            self.__setNextFrame()
    
    def __setNextFrame(self):
        success, frame = self.cap.read()
        # try read from start
        if not success:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, frame = self.cap.read()
        # failed to read stop
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

    def restartVideo(self):
        self.delta = 0
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
