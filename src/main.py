import numpy as np
from numpy.linalg import norm
width = 1280
height = 720

import time

start = time.time()


from graphicPipeline import GraphicPipeline


pipeline = GraphicPipeline(width, height)


from projection import Projection
from camera_v2 import camera_v2_mat

cam_position = np.array([1.1, 1.1, 1.1])
target = np.array([0, 0, 0])
d_up = np.array([0, 0, 1])

# +front -back 
# +left ear -right ear
# +up -down
lightPosition = np.array([1.1, -1.1, 1.1])

mat_view = camera_v2_mat(cam_position, target, d_up)
mat_shadow = camera_v2_mat(lightPosition, np.array([0, 0, 0]), np.array([0, 0, 1]))

nearPlane = 0.1
farPlane = 10.0
fov = 1.91986
aspectRatio = width / height

proj = Projection(nearPlane, farPlane, fov, aspectRatio)


from readply import readply

vertices, triangles = readply("../data/suzanne.ply")


# load and show an image with Pillow
from PIL import Image
from numpy import asarray

# Open the image form working directory
image = asarray(Image.open("../data/suzanne.png"))


data = {
    "viewMatrix": mat_view,
    "projMatrix": proj.getMatrix(),
    "cameraPosition": cam_position,
    "lightPosition": lightPosition,
    "is_shadow": False,
    "texture": image,
}


data_shadow = {
    "viewMatrix": mat_shadow,
    "projMatrix": proj.getMatrix(),
    "cameraPosition": lightPosition,
    "lightPosition": lightPosition,
    "is_shadow": True,
    "texture": image,
}

from copy import deepcopy
import matplotlib.pyplot as plt

start = time.time()

# Première vue
pipeline1 = GraphicPipeline(width, height)
pipeline1.draw(vertices, triangles, data)
image1 = deepcopy(pipeline1.image)

# Deuxième vue (nouvelle instance pour éviter les artefacts)
pipeline2 = GraphicPipeline(width, height)
pipeline2.draw(vertices, triangles, data_shadow)
image2 = deepcopy(pipeline2.image)

# Affichage côte à côte
plt.subplot(1, 2, 1)
plt.imshow(image1)
plt.title("Vue cam")

plt.subplot(1, 2, 2)
plt.imshow(image2)
plt.title("Vue shadow")
plt.show()

end = time.time()
print(end - start)
