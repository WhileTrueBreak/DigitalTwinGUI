from vedo import *

transform = np.identity(4)

mesh = Mesh("res/models/teapot.obj")
# mesh.texture("res/textures/AMW_RIGHT.png")
mesh = mesh.triangulate()
mesh.compute_normals()

vertices = mesh.vertices
verticesT = np.ones((mesh.npoints, 4))
verticesT[::,0:3] = vertices
verticesT = transform.dot(verticesT.T)
vertices = verticesT.T[::,0:3]
normals = mesh.vertex_normals
normalsT = np.zeros((mesh.npoints, 4))
normalsT[::,0:3] = normals
normalsT = transform.dot(normalsT.T)
normals = normalsT.T[::,0:3]
uvs = mesh.pointdata[mesh.pointdata.keys()[0]]
vs = np.hstack((vertices, normals))
if uvs.shape[1] == 2:
    vs = np.hstack((vs, uvs))
indices = np.array(mesh.cells).flatten()

mesh.show()

print(vs)
