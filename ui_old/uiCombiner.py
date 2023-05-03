from ui.uiElement import GlElement
from ui.constraintManager import *

from asset import *
import math

class UiCombiner(GlElement):
    def __init__(self, window, constraints, dim=(0,0,0,0)):
        constraints = constraints.copy()
        constraints.append(ABSOLUTE(T_W, 0))
        constraints.append(ABSOLUTE(T_H, 0))
        super().__init__(window, constraints, dim)
        self.prevDim = (0,0)
    
    def updateDim(self):
        relDim = self.parent.constraintManager.calcConstraints(*self.constraints)
        self.dim = (relDim[0] + self.parent.dim[0], relDim[1] + self.parent.dim[1], relDim[2], relDim[3])
        self.openGLDim = (
            (2*self.dim[0])/self.window.dim[0] - 1,
            (2*(self.window.dim[1]-self.dim[1]-self.dim[3]))/self.window.dim[1] - 1,
            (2*self.dim[2])/self.window.dim[0],
            (2*self.dim[3])/self.window.dim[1],
        )
        self.constraintManager.pos = (self.dim[0], self.dim[1])
        # print(self.parent.dim[2], self.parent.dim[3])
        self.constraintManager.dim = (self.parent.dim[2], self.parent.dim[3])

    def reshape(self):
        return

    def absUpdate(self, delta):
        minx, miny = math.inf, math.inf
        maxx, maxy = -math.inf, -math.inf
        childQueue = self.children.copy()
        while len(childQueue) != 0:
            child = childQueue[0]
            childQueue.remove(child)
            childQueue.extend(child.children)
            if child.dim[0] < minx:
                minx = child.dim[0]
            if child.dim[1] < miny:
                miny = child.dim[1]
            if child.dim[0]+child.dim[2] > maxx:
                maxx = child.dim[0]+child.dim[2]
            if child.dim[1]+child.dim[3] > maxy:
                maxy = child.dim[1]+child.dim[3]
        print(minx, miny, maxx, maxy)
        if self.prevDim == (maxx-minx, maxy-miny):
            return
        self.prevDim = (maxx-minx, maxy-miny)
        self.updateWidth(ABSOLUTE(T_W, maxx-minx))
        self.updateHeight(ABSOLUTE(T_H, maxy-miny))
        return

    def absRender(self):
        return