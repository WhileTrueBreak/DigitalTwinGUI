from ui.elements.uiWrapper import UiWrapper
from ui.uiBatch import UiBatch

from utils.timing import *

class UiLayer:

    MAX_BATCH_SIZE = 128

    def __init__(self, window):
        self.window = window
        
        self.masterElem = UiWrapper(self.window, [], (0, 0, *window.dim))

        self.hasMasterListChanged = False
        self.masterList = []

        self.batches = []
    
    def update(self, delta):
        if self.window.resized:
            for batch in self.batches:
                batch.updateFrame()
            self.__updateMasterElem()
        if self.masterElem.isDirtyComponents:
            self.__updateMasterList()
        if self.hasMasterListChanged:
            self.__updateRenderers()
        self.masterElem.update(delta)

    def render(self):
        for batch in self.batches:
            batch.render()
        return

    @timing
    def __updateRenderers(self):
        self.batches = []
        currentBatch = None
        for i in range(len(self.masterList)):
            elem = self.masterList[i]
            for renderer in elem.getRenderers():
                if currentBatch == None or not currentBatch.hasRoom(renderer):
                    currentBatch = UiBatch(self.window, UiLayer.MAX_BATCH_SIZE)
                    self.batches.append(currentBatch)
                renderer.setId(i)
                currentBatch.addRenderer(renderer)
        self.hasMasterListChanged = False

    @timing
    def __updateMasterList(self):
        self.masterList = []
        queue = [self.masterElem]
        while len(queue) > 0:
            elem = queue.pop(0)
            self.masterList.append(elem)
            queue.extend(elem.children)
        self.masterList = sorted(self.masterList, key=lambda a:a.getZIndex())
        self.masterElem.setCleanComponents()
        self.hasMasterListChanged = True

    @timing
    def __updateMasterElem(self):
        self.masterElem.dim = (0,0,*self.window.dim)
        self.masterElem.childConstraintManager.pos = (0,0)
        self.masterElem.childConstraintManager.dim = self.window.dim
        self.masterElem.setDirtyVertices()

    def getMasterElem(self):
        return self.masterElem

    def getScreenSpaceUI(self, x, y):
        data = (0,0,0)
        for batch in self.batches:
            d = batch.getScreenSpaceUI(x, y)
            if d[0] == 0:
                continue
            data = d
        if (data[0]-1) == -1:
            return None
        element = self.masterList[data[0]-1]
        while element.getLinkedElement() != element:
            element = element.getLinkedElement()
        return element

