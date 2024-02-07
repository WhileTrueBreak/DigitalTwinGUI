from ui.glElement import GlElement
from ui.uiRenderer import UiRenderer
from utils.transform import Transform
from utils.debug import *

from asset import *

import ctypes

class UiToggleButton(GlElement):
    def __init__(self, window, constraints, dim=(0,0,0,0)):
        super().__init__(window, constraints, dim)
        self.type = 'button'

        self.mask = None
        self.currentColor = (1, 1, 1)
        self.untoggledColor = (1, 1, 1)
        self.toggleColor = (0.8, 0.8, 0.8)
        self.lockColor = (1, 1, 1)

        self.toggled = False

        self.renderer = UiRenderer.fromColor(self.currentColor, Transform.fromPS((self.openGLDim[0:2]),(self.openGLDim[2:4])))
        self.renderers.append(self.renderer)

        self.lockFlag = False

    def reshape(self):
        self.renderer.setColor(self.currentColor)
        self.renderer.setTexture(self.mask)
        self.renderer.getTransform().setPos((self.openGLDim[0:2]))
        self.renderer.getTransform().setSize((self.openGLDim[2:4]))
        self.renderer.setDirtyVertex()
        return

    def update(self, delta):
        self.currentColor = self.toggleColor if self.toggled else self.untoggledColor
        return

    def __setColor(self, color):
        if self.currentColor == color:
            return
        self.currentColor = color
        self.reshape()
        return

    def isToggled(self):
        return self.toggled

    def setToggle(self, toggle):
        self.toggled = toggle
        self.update(0)

    def setUntoggleColor(self, color):
        self.untoggledColor = color
        self.update(0)

    def setToggleColor(self, color):
        self.toggleColor = color
        self.update(0)

    def setLockColor(self, color):
        self.lockColor = color
        self.update(0)
    
    def setMaskingTexture(self, texture):
        self.mask = texture
        self.reshape()

    def onDefault(self, callback=None):
        if self.lockFlag: return
        self.__setColor(self.currentColor)
    
    def onHover(self, callback=None):
        if self.lockFlag: return
    
    def onHeld(self, callback=None):
        if self.lockFlag: return

    def onPress(self, callback=None):
        if self.lockFlag: return
        self.window.uiEvents.append({'obj':self, 'action':'press', 'type':self.type, 'time':time.time_ns()})
    
    def onRelease(self, callback=None):
        if self.lockFlag: return
        self.toggled = not self.toggled
        self.__setColor(self.toggleColor if self.toggled else self.untoggledColor)
        self.window.uiEvents.append({'obj':self, 'action':'release', 'type':self.type, 'time':time.time_ns()})

    def lock(self):
        self.lockFlag = True
        self.__setColor(self.lockColor)
        
    def unlock(self):
        self.lockFlag = False
        self.__setColor(self.toggleColor if self.toggled else self.untoggledColor)
        