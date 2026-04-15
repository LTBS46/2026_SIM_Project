import numpy as np
from numpy.linalg import norm
import time
from PIL import Image
from numpy import asarray
from copy import deepcopy
from math import sqrt
import matplotlib.pyplot as plt
from graphicPipeline import GraphicPipeline
from projection import Projection
from orthographic_projection import OrthographicProjection
from readply import readply
from camera_v2 import camera_v2_mat


width = 1280
height = 720

pipeline = GraphicPipeline(width, height)

cam_position = np.array([1.1, 1.1, 1.1])
target = np.array([0, 0, 0])
d_up = np.array([0, 0, 1])
light_target = target

# +front -back 
# +left ear -right ear
# +up -down
# lightPosition = np.array([0.01, 0.01, 1.5])
lightPosition = np.array([1.1, -1.1, 1.1])

mat_view = camera_v2_mat(cam_position, target, d_up)
mat_shadow = camera_v2_mat(lightPosition, light_target, d_up)

nearPlane = 0.1
farPlane = 10.0
fov = 1.91986
aspectRatio = width / height

proj = Projection(nearPlane, farPlane, fov, aspectRatio)

entries = ["../data/suzanne.ply", "../data/floor.ply"]

v_entries = []
t_entries = []

v_off = 0
tex_id = 0

for __entry in entries:
    c_vert, c_tri = readply(__entry)
    c_vert2 = np.zeros((len(c_vert), 9))
    c_vert2[:, :8] = c_vert[:, :]
    c_vert2[:, 8] = tex_id
    c_tri += v_off
    v_off += len(c_vert)
    v_entries.append(c_vert2)
    t_entries.append(c_tri)
    tex_id += 1

vertices = np.concatenate(v_entries)
triangles = np.concatenate(t_entries)


ltn = np.linalg.norm(light_target - lightPosition)
ltr = (light_target - lightPosition) / ltn

max_d = 0.0
for vertice in vertices:
    vert = vertice[:3]
    vtn = norm(vert)
    vtr = vert / vtn
    nd = sqrt(sum((vert - light_target) ** 2))
    ndt = abs(np.dot(ltr, vtr))
    nd *= ndt
    if nd > max_d:
        max_d = nd

print(f"{max_d=}")
        
proj_shadow = OrthographicProjection(-nearPlane, -farPlane, -max_d, max_d, max_d, -max_d)

# load and show an image with Pillow
# Open the image form working directory
image = asarray(Image.open("../data/suzanne.png"))

data_shadow = {
    "viewMatrix": mat_shadow,
    "projMatrix": proj_shadow.getMatrix(),
    "cameraPosition": lightPosition,
    "lightPosition": lightPosition,
    "is_shadow": True,
}

print(f"{np.ones((1, 1, 3)) = }")

data = {
    "viewMatrix": mat_view,
    "projMatrix": proj.getMatrix(),
    "cameraPosition": cam_position,
    "lightPosition": lightPosition,
    "textures": [image, np.ones((1, 1, 3))*255],
    "shadowView": mat_shadow,
    "shadowProj": proj_shadow.getMatrix()
}

start = time.time()

# Vue shadow
pipeline2 = GraphicPipeline(1080, 1080)

# Suzanne
pipeline2.draw(vertices, triangles, data_shadow)

image2 = -deepcopy(pipeline2.image)

end = time.time()
print("time: ", end - start)
start = end

data["shadowMap"] = image2

# Rendu final
pipeline1 = GraphicPipeline(width, height)

# Suzanne
data["useTexture"] = True
pipeline1.draw(vertices, triangles, data)

image1 = deepcopy(pipeline1.image)

end = time.time()
print("time: ", end - start)

# Affichage côte à côte
plt.subplot(1, 2, 1)
plt.imshow(image1)
plt.title("Rendu")

plt.subplot(1, 2, 2)
plt.imshow(image2)
plt.title("Depth map")
plt.show()

