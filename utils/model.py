import time
import os

from stl import mesh as stlmesh
import pywavefront
import numpy as np

class Model:

    @classmethod
    def fromSTL(cls, file, transform=np.identity(4)):
        # try:
        mesh = stlmesh.Mesh.from_file(file)
        # except Exception:
        #     raise Exception(f'Error loading stl: {file}')
        numVertices = len(mesh.vectors) * 3
        vertices = np.zeros((numVertices, 8), dtype='float32')
        indices = np.zeros(numVertices, dtype='float32')

        normals = np.cross(mesh.vectors[::, 1] - mesh.vectors[::, 0], mesh.vectors[::, 2] - mesh.vectors[::, 0])
        vectors = np.zeros((normals.shape[0], 4))
        vectors[::, 0:3] = normals
        vectors = transform.dot(vectors.T)
        normals = vectors.T[::, 0:3]
        normals /= np.sqrt((normals ** 2).sum(-1))[..., np.newaxis]
        normals = np.repeat(normals, 3, axis=0)
        vertices[::,3:6] = normals
        
        flattened = mesh.vectors.reshape(mesh.vectors.shape[0]*3, 3)
        vectors = np.ones((flattened.shape[0], 4))
        vectors[::,0:3] = flattened
        vectors = transform.dot(vectors.T)
        vertices[::,0:3] = vectors.T[::,0:3]

        return [cls(vertices, indices)]

    @classmethod
    def fromOBJ(cls, file, transform=np.identity(4)):
        scene = pywavefront.Wavefront(file, parse=True)
        models = []
        materials = list(scene.materials.items().mapping.values())
        for material in materials:
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
            models.append(cls(vertices, indices))
        return models

    @classmethod
    def fromVertices(cls, vertices, transform=np.identity(4)):
        return [cls(vertices, np.arange(len(vertices)))]

    def __init__(self, vertices, indices):
        self.vertices = vertices
        self.indices = indices
        self.createVertexData(self.vertices)
    
    def createVertexData(self, vertices):
        vertices = np.array(vertices,dtype='float32')
        has_uvs = False
        if len(vertices[0]) == 5:
            has_uvs = True
            uvs = np.array(vertices[::,3:5])

        vertices = np.array(vertices[::,0:3])
        self.vertices = np.zeros((len(vertices), 8))
        self.vertices[::, 0:3] = vertices

        normals = np.cross(vertices[1::3] - vertices[0::3], vertices[2::3] - vertices[0::3])
        normals /= np.sqrt((normals ** 2).sum(-1))[..., np.newaxis]
        normals = np.repeat(normals, 3, axis=0)
        self.vertices[::,3:6] = normals
        if has_uvs:
            self.vertices[::,6:8] = uvs
