from scenes.models.iModel import IModel
from scenes.ui.pages import Pages

from ui.constraintManager import *
from ui.elements.uiButton import UiButton
from ui.elements.uiWrapper import UiWrapper
from ui.elements.ui3dScene import Ui3DScene
from ui.elements.uiStream import UiStream
from ui.elements.uiWrapper import UiWrapper
from ui.elements.uiText import UiText
from ui.elements.uiSlider import UiSlider

class GenericModel(IModel):

    def __init__(self, window, renderer, model, transform):
        self.window = window
        self.renderer = renderer
        self.transform = transform
        self.modelId = self.renderer.addModel(model, transform)
        self.__createUi()
        return

    def __createUi(self):
        self.pages = Pages(self.window, Constraints.ALIGN_PERCENTAGE(0, 0, 1, 1))
        self.pages.addPage()
        movePage = self.pages.getPage(0)
        self.title = UiText(self.window, Constraints.ALIGN_CENTER_PERCENTAGE(0.5, 0.05))
        self.title.setText('Move')
        self.title.setTextColor((1,1,1))
        self.title.setFontSize(28)
        movePage.addChild(self.title)

        wrapper = UiWrapper(self.window, [
            *Constraints.ALIGN_CENTER,
            RELATIVE(T_W, 1, P_W),
            RELATIVE(T_H, 1, T_W),
        ])
        movePage.addChild(wrapper)
        
        self.buttons = []
        self.buttons.append(UiButton(self.window, Constraints.ALIGN_PERCENTAGE_PADDING(0.0,0.3,0.3,0.3,2)))
        self.buttons.append(UiButton(self.window, Constraints.ALIGN_PERCENTAGE_PADDING(0.3,0.0,0.3,0.3,2)))
        self.buttons.append(UiButton(self.window, Constraints.ALIGN_PERCENTAGE_PADDING(0.3,0.6,0.3,0.3,2)))
        self.buttons.append(UiButton(self.window, Constraints.ALIGN_PERCENTAGE_PADDING(0.6,0.3,0.3,0.3,2)))
        wrapper.addChildren(*self.buttons)
        return

    def update(self):
        return

    def handleEvents(self, event):
        if event['action'] == 'release':
            if not event['obj'] in self.buttons: return
            index = self.buttons.index(event['obj'])
            self.__move(index)
        return
    
    def __move(self, index):
        d = 0.1
        m = {0:(-d,0),1:(0,d),2:(0,-d),3:(d,0)}
        x,y,z = self.getPos()
        self.setPos((x+m[index][0], y+m[index][1], z))

    def getControlPanel(self):
        return self.pages.getPageWrapper()

    def isModel(self, modelId):
        return modelId == self.modelId
    
    def getPos(self):
        return self.transform[0:3,3]
    
    def setPos(self, pos):
        self.transform[0:3,3] = pos
        self.renderer.setTransformMatrix(self.modelId, self.transform)
        return