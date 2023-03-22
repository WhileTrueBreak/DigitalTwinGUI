from ui.uiButton import UiButton
from ui.uiStream import UiStream
from ui.uiVideo import UiVideo
from ui.uiTextInput import UiTextInput

from utils.uiHelper import *

from constraintManager import *
from scenes.scene import *

class CamScene(Scene):
    
    def __init__(self, window, name):
        super().__init__(window, name)
        self.isDisplayed = False
        self.camBtns = []
        self.streams = []

    def createUi(self):
        btnPadding = 5

        constraints = [
            COMPOUND(RELATIVE(T_X, 0.5, P_W), ABSOLUTE(T_X, btnPadding)),
            ABSOLUTE(T_Y, btnPadding),
            COMPOUND(RELATIVE(T_W, 0.5, P_W), ABSOLUTE(T_W, -2 * btnPadding)),
            RELATIVE(T_H, 3/4, T_W)
        ]
        self.streams.append(UiStream(self.window, constraints, 'http://172.31.1.225:8080/?action=streams'))
        self.streams.append(UiStream(self.window, constraints, 'http://172.31.1.226:8080/?action=streams'))

        for i in range(len(self.streams)):
            constraints = [
                COMPOUND(RELATIVE(T_X, 0, P_W), ABSOLUTE(T_X, btnPadding)),
                COMPOUND(ABSOLUTE(T_Y, (30 + 2 * btnPadding)*i), ABSOLUTE(T_Y, btnPadding)),
                COMPOUND(RELATIVE(T_W, 0.25, P_W), ABSOLUTE(T_W, -2 * btnPadding)),
                ABSOLUTE(T_H, 30)
            ]
            btn, text = centeredTextButton(self.window, constraints)
            btn.setDefaultColor((0.9,0.9,0.9))
            btn.setHoverColor((1,1,1))
            btn.setPressColor((0.9,1,1))
            text.setText(f'stream {i+1}')
            text.setFontSize(24)
            text.setTextSpacing(7)
            text.setTextColor((0,0,0))
            self.camBtns.append(btn)
        self.sceneWrapper.addChildren(*self.camBtns)

        constraints = [
            ABSOLUTE(T_X, 5),
            COMPOUND(COMPOUND(RELATIVE(T_Y, 1, P_H), RELATIVE(T_Y, -1, T_H)), ABSOLUTE(T_Y, -5)),
            RELATIVE(T_W, 0.3, P_W),
            ABSOLUTE(T_H, 24),
        ]

        self.textBox = UiTextInput(self.window, constraints)
        self.textBox.setRegex(r'^.{,20}$')
        self.textBox.setFontSize(18)
        self.textBox.setTextSpacing(6)
        self.textBox.setBorderWeight(2)
        self.sceneWrapper.addChild(self.textBox)

    def handleUiEvents(self, event):
        if event['action'] == 'release':
            for i in range(len(self.streams)):
                if event['obj'] != self.camBtns[i]: continue
                self.sceneWrapper.removeChildren(*self.streams)
                for stream in self.streams:
                    stream.stop()
                self.sceneWrapper.addChild(self.streams[i])
                self.streams[i].start()
        return
    
    def absUpdate(self, delta):
        return

    def start(self):
        for stream in self.streams:
            stream.start()
        return
    
    def stop(self):
        for stream in self.streams:
            stream.stop()
        return


