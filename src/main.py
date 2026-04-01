import numpy as np
from numpy.linalg import norm
import time
from PIL import Image
from numpy import asarray
from copy import deepcopy
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
lightPosition = np.array([1.1, -1.1, 1.1])

mat_view = camera_v2_mat(cam_position, target, d_up)
mat_shadow = camera_v2_mat(lightPosition, light_target, np.array([0, 0, 1]))

nearPlane = 0.1
farPlane = 10.0
fov = 1.91986
aspectRatio = width / height

proj = Projection(nearPlane, farPlane, fov, aspectRatio)



vertices, triangles = readply("../data/suzanne.ply")

max_d = 0.0

for vertice in vertices:
    vert = vertice[:3]
    nd = sum((vert - light_target) ** 2)
    if nd > max_d:
        max_d = nd

# load and show an image with Pillow
# Open the image form working directory

image = asarray(Image.open("../data/suzanne.png"))

data_shadow = {
    "viewMatrix": mat_shadow,
    "projMatrix": proj.getMatrix(),
    "cameraPosition": lightPosition,
    "lightPosition": lightPosition,
    "is_shadow": True,
}

data = {
    "viewMatrix": mat_view,
    "projMatrix": proj.getMatrix(),
    "cameraPosition": cam_position,
    "lightPosition": lightPosition,
    "texture": image,
    "shadowView": mat_shadow,
    "shadowProj": proj.getMatrix()
}

start = time.time()


# Deuxième vue (nouvelle instance pour éviter les artefacts)
pipeline2 = GraphicPipeline(width, height)
pipeline2.draw(vertices, triangles, data_shadow)
image2 = deepcopy(pipeline2.image)

end = time.time()
print("time: ", end - start)
start = end

data["shadowMap"] = image2

# Première vue
pipeline1 = GraphicPipeline(width, height)
pipeline1.draw(vertices, triangles, data)
image1 = deepcopy(pipeline1.image)

end = time.time()
print("time: ", end - start)

# Affichage côte à côte
plt.subplot(1, 2, 1)
plt.imshow(image1)
plt.title("Vue cam")

plt.subplot(1, 2, 2)
plt.imshow(image2)
plt.title("Vue shadow")
plt.show()

