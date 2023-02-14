from stl import mesh
import numpy as np
import time


class Model:
    def __init__(self, file=None, vertices=None, transform=np.identity(4)):
        if file != None:
            self.file = file
            self.mesh = self.loadSTL(file)
            self.vertices, self.indices = self.createVertices(transform)
        if vertices != None:
            self.createVertexData(vertices)
            self.indices = np.arange(len(self.vertices))
    
    def loadSTL(self, file):
        try:
            return mesh.Mesh.from_file(file)
        except Exception:
            raise Exception(f'Error loading stl: {file}')
    
    def createVertexData(self, vertices):
        vertices = np.array(vertices)
        self.vertices = np.zeros((len(vertices), 6))
        self.vertices[::, 0:3] = vertices

        normals = np.cross(vertices[1::3] - vertices[0::3], vertices[2::3] - vertices[0::3])
        normals /= np.sqrt((normals ** 2).sum(-1))[..., np.newaxis]
        normals = np.repeat(normals, 3, axis=0)
        self.vertices[::,3:6] = normals

    def createVertices(self, transformationMatrix):
        start = time.time_ns()
        numVertices = len(self.mesh.vectors) * 3
        vertices = np.zeros((numVertices, 6), dtype='float32')
        indices = np.zeros(numVertices, dtype='float32')

        normals = np.cross(self.mesh.vectors[::, 1] - self.mesh.vectors[::, 0], self.mesh.vectors[::, 2] - self.mesh.vectors[::, 0])
        vectors = np.zeros((normals.shape[0], 4))
        vectors[::, 0:3] = normals
        vectors = transformationMatrix.dot(vectors.T)
        normals = vectors.T[::, 0:3]
        normals /= np.sqrt((normals ** 2).sum(-1))[..., np.newaxis]
        normals = np.repeat(normals, 3, axis=0)
        vertices[::,3:6] = normals
        
        flattened = self.mesh.vectors.reshape(self.mesh.vectors.shape[0]*3, 3)
        vectors = np.ones((flattened.shape[0], 4))
        vectors[::,0:3] = flattened
        vectors = transformationMatrix.dot(vectors.T)
        vertices[::,0:3] = vectors.T[::,0:3]

        return (vertices, indices)

