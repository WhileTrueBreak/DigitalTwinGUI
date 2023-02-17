from ui.uiButton import UiButton
from ui.uiStream import UiStream
from ui.uiVideo import UiVideo

from ui.uiHelper import *
from constraintManager import *
from scenes.scene import *

class BadApple(Scene):
    
    def __init__(self, window, name):
        super().__init__(window, name)

    def createUi(self):
        padding = 20
        constraints = [
            ABSOLUTE(T_X, padding),
            ABSOLUTE(T_Y, padding),
            COMPOUND(RELATIVE(T_W, 1, P_W), ABSOLUTE(T_W, -2*padding)),
            RELATIVE(T_H, 720/1280, T_W)
        ]
        self.video = UiVideo(self.window, constraints)
        self.video.setVideo(Assets.BAD_APPLE_VID)
        self.sceneWrapper.addChild(self.video)

    def handleUiEvents(self, event):
        return
    
    def absUpdate(self, delta):
        return

    def start(self):
        return
    
    def stop(self):
        return


