from OpenGL import GL
from stl import mesh
import numpy as np
import ctypes
import time

from mathHelper import normalize


class Model:
    def __init__(self, file, shader, transform=np.identity(4)):
        self.file = file
        self.isDirty = True
        self.color = [1,1,1]
        self.shader = shader
        self.mesh = self.loadSTL(file)
        self.vertices, self.indices = self.createVertices(transform)
        # self.projectionMatrix = np.identity(4)
        # self.viewMatrix = np.identity(4)
    
    def loadSTL(self, file):
        try:
            return mesh.Mesh.from_file(file)
        except Exception:
            raise Exception(f'Error loading stl: {file}')
    
    def createVertices(self, transformationMatrix):
        numVertices = len(self.mesh.vectors) * 3
        vertices = np.zeros((numVertices, 6), dtype='float32')
        indices = np.zeros(numVertices, dtype='float32')

        counter = 0
        for face in self.mesh.vectors:
            v1 = np.subtract(face[1], face[0])
            v2 = np.subtract(face[2], face[0])
            normal = normalize(np.cross(v1, v2))
            tnormal = transformationMatrix.dot([*normal, 0])
            for i in range(3):
                if counter % 10000 == 0:
                    print(f'{self.file}: {(counter/(len(self.mesh.vectors)*3)*100):.0f}% done')
                tface = transformationMatrix.dot([*face[i], 1])
                vertices[counter, 0:3] = tface[:-1]
                vertices[counter, 3:6] = tnormal[:-1]
                indices[counter] = counter
                counter += 1
        return (vertices, indices)

    def setColor(self, color):
        self.color = color
        self.isDirty = True
