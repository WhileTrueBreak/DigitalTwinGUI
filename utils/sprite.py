class Sprite:

    def __init__(self, texture, coords):
        self.texture = texture
        self.texCoords = coords
    
    @classmethod
    def fromTexture(cls, texture):
        return cls(texture, [(1,1), (1,0), (0,0), (0,1)])
    
    def getTexture(self):
        return self.texture
    
    def getTexCoords(self):
        return self.texCoords

