from utils.sprite import Sprite

class UiRenderer:

    def __init__(self, color, sprite, transform):
        self.parentUi = None
        self.color = color
        self.sprite = sprite
        self.transform = transform
        self.isDirtyVertex = True
        self.isDirtySprite = True
    
    @classmethod
    def fromColor(cls, color, transform):
        if len(color) == 3:
            color = (*color, 1)
        return cls(color, Sprite.fromTexture(None), transform)
    
    @classmethod
    def fromSprite(cls, sprite, transform):
        return cls((1,1,1,1), sprite, transform)
    
    def getTransform(self):
        return self.transform

    def getTexCoords(self):
        return self.sprite.getTexCoords()

    def getTexture(self):
        return self.sprite.getTexture()

    def getColor(self):
        return self.color
    
    def getSprite(self):
        return self.sprite

    def setColor(self, color):
        if len(color) == 3:
            color = (*color, 1)
        if color == self.color: 
            return
        self.color = color
        self.isDirtyVertex = True
    
    def setSprite(self, sprite):
        self.sprite = sprite
        self.isDirtySprite = True
    
    def setCleanVertex(self):
        self.isDirtyVertex = False

    def setCleanSprite(self):
        self.isDirtySprite = False
    
    def getParentUi(self):
        return self.parentUi

    def setParentUi(self, ui):
        self.parentUi = ui

