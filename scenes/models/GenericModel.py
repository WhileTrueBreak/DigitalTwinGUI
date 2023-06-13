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
        return

    def update(self):
        return

    def handleEvents(self, event):
        return

    def getControlPanel(self):
        return self.pages.getPageWrapper()

    def isModel(self, modelId):
        return modelId == self.modelId
    
    def getPos(self):
        return self.transform[0:3,3]
    
    def setPos(self, pos):
        self.transform[0:3,3] = pos
        self.modelRenderer.setTransformMatrix(self.modelId, self.transform)
        return