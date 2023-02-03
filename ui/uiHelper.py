from ui.uiElement import *
from constraintManager import *

def centeredTextButton(window, constraints, shader):
    btn = UiButton(window, constraints, shader)

    textConstraints = [
        COMPOUND(RELATIVE(T_X, -0.5, T_W), RELATIVE(T_X, 0.5, P_W)),
        COMPOUND(RELATIVE(T_Y, -0.5, T_H), RELATIVE(T_Y, 0.5, P_H))
    ]
    text = UiText(window, textConstraints)
    btn.addChild(text)
    return (btn, text)


