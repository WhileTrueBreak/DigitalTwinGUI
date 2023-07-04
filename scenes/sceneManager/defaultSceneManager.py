from scenes.sceneManager.sceneManager import SceneManager
from ui.constraintManager import *

from ui.elements.uiWrapper import UiWrapper
from ui.elements.uiButton import UiButton
from ui.elements.uiBlock import UiBlock
from ui.elements.ui3dScene import Ui3DScene
from ui.uiHelper import *

from asset import *

class DefaultSceneManager(SceneManager):

    def __init__(self):
        super().__init__()
    
    def createUi(self):
        constraints = [ABSOLUTE(T_X, 0),
                       ABSOLUTE(T_Y, 0),
                       RELATIVE(T_W, 1, P_W),
                       ABSOLUTE(T_H, 40)]
        self.tabWrapper = UiWrapper(self.window, constraints)
        self.wrapper.addChild(self.tabWrapper)
        constraints = [ABSOLUTE(T_X, 0),
                       ABSOLUTE(T_Y, 40),
                       RELATIVE(T_W, 1, P_W),
                       COMPOUND(RELATIVE(T_H, 1, P_H), ABSOLUTE(T_H, -40))]
        self.sceneWrapper = UiWrapper(self.window, constraints)
        self.wrapper.addChild(self.sceneWrapper)
        
        numBtns = len(self.scenes)

        for i in range(numBtns):
            constraints = [
                COMPOUND(RELATIVE(T_Y, -0.5, T_H), RELATIVE(T_Y, 0.5, P_H)),
                COMPOUND(RELATIVE(T_X, -0.5, T_W), RELATIVE(T_X, 0.5/numBtns + 1/numBtns * i, P_W)),
                RELATIVE(T_H, 0.9, P_H),
                COMPOUND(RELATIVE(T_W, 1/numBtns, P_W), RELATIVE(T_W, -0.1, P_H))
            ]
            btn, text = centeredTextButton(self.window, constraints)
            text.setText(f'{self.scenes[i].name}')
            text.setFontSize(24)
            text.setTextSpacing(6)
            text.setTextColor((1,1,1))
            text.setFont(Assets.ARIAL_FONT)
            btn.setDefaultColor([0,109/255,174/255])
            btn.setHoverColor([0,159/255,218/255])
            btn.setPressColor([0,172/255,62/255])
            self.sceneMap[btn] = self.scenes[i]
            self.btns.append(btn)
        self.tabWrapper.addChildren(*self.btns)
        self.setScene(self.scenes[0])