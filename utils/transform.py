class Transform:
    
    def __init__(self, pos, size, rotPoint, rot):
        self.parentRenderer = None
        self.pos = pos
        self.size = size
        self.rotPoint = rotPoint
        self.rot = rot
    
    @classmethod
    def blank(cls):
        return cls((0,0), (0,0), (0,0), 0)
    
    @classmethod
    def fromP(cls, pos):
        return cls(pos, (0,0), (0,0), 0)
    
    @classmethod
    def fromPS(cls, pos, size):
        return cls(pos, size, (0,0), 0)
    
    @classmethod
    def fromPSR(cls, pos, size, rotPoint, rot):
        return cls(pos, size, rotPoint, rot)
    
    def getVertices(self):
        x,y = self.pos
        w,h = self.size
        return [
            (x,y),
            (x+w,y),
            (x+w,y+h),
            (x,y+h)
        ]

    def copy(self):
        return Transform(self.pos, self.size, self.rotPoint, self.rot)
    
    def setPos(self, pos):
        if self.parentRenderer != None:
            self.parentRenderer.isDirtyVertex = True
        self.pos = pos

    def setSize(self, size):
        if self.parentRenderer != None:
            self.parentRenderer.isDirtyVertex = True
        self.size = size
    
    def setRotPoint(self, point):
        if self.parentRenderer != None:
            self.parentRenderer.isDirtyVertex = True
        self.rotPoint = point
    
    def setRot(self, rot):
        self.rot = rot
