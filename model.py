from stl import mesh
import pywavefront
import numpy as np
import time
import os


class Model:
    def __init__(self, file=None, vertices=None, transform=np.identity(4)):
        if file != None:
            self.file = file
            self.loadFile(transform)
        if vertices != None:
            self.createVertexData(vertices)
            self.indices = np.arange(len(self.vertices))
    
    def loadFile(self, transform):
        ext = os.path.splitext(self.file)[1].lower()
        if ext == '.stl':
            self.mesh = self.loadSTL(self.file)
            self.vertices, self.indices = self.createVertices(transform)
        elif ext == '.obj':
            self.vertices, self.indices = self.loadOBJ(self.file, transform)
        else:
            raise Exception(f'Can not load file type: {ext}')

    def loadSTL(self, file):
        try:
            return mesh.Mesh.from_file(file)
        except Exception:
            raise Exception(f'Error loading stl: {file}')
    
    def loadOBJ(self, file, transform):
        scene = pywavefront.Wavefront(self.file, parse=True)
        
        material = list(scene.materials.items().mapping.values())[0]

        index = [0,1,2,3,3,3,3,3]
        if material.has_uvs and material.has_normals:
            index = [5,6,7,2,3,4,0,1]
        elif material.has_uvs:
            index = [2,3,4,5,5,5,0,1]
        elif material.has_normals:
            index = [3,4,5,0,1,2,6,6]
        vertexSize = material.vertex_size
        vertices = np.array(material.vertices,dtype='float32')
        numVertices = int(len(vertices)/vertexSize)

        indices = np.zeros(numVertices, dtype='float32')
        vertices = vertices.reshape(numVertices, vertexSize)

        zeros = np.zeros((numVertices,1))
        neg = np.tile([-1], (numVertices,1))
        vertices = np.append(vertices, zeros, axis=1)
        vertices = vertices[::,index]
        # generate normal if they dont exist
        if not material.has_normals:
            normals = np.cross(vertices[0::3,0:3] - vertices[1::3,0:3], vertices[0::3,0:3] - vertices[2::3,0:3])
            normals = np.repeat(normals, 3, axis=0)
            vertices[::,3:6] = normals
        # update vertices based on transfromation matrix
        vectors = np.zeros((numVertices, 4))
        vectors[::, 0:3] = vertices[::,3:6]
        vectors = transform.dot(vectors.T)
        vectors = vectors.T[::,0:3]
        vectors /= np.sqrt((vectors ** 2).sum(-1))[..., np.newaxis]
        vertices[::,3:6] = vectors

        vectors = np.ones((numVertices, 4))
        vectors[::, 0:3] = vertices[::,0:3]
        vectors = transform.dot(vectors.T)
        vertices[::,0:3] = vectors.T[::,0:3]
        return vertices, indices

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
        vertices = np.zeros((numVertices, 8), dtype='float32')
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

