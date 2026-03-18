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

t2 = camera_v2_mat(cam_position, target, d_up)

nearPlane = 0.1
farPlane = 10.0
fov = 1.91986
aspectRatio = width / height

proj = Projection(nearPlane, farPlane, fov, aspectRatio)

# +front -back 
# +left ear -right ear
# +up -down
lightPosition = np.array([0, 10, 0])

from readply import readply

vertices, triangles = readply("../data/suzanne.ply")


# load and show an image with Pillow
from PIL import Image
from numpy import asarray

# Open the image form working directory
image = asarray(Image.open("../data/suzanne.png"))


data = {
    "viewMatrix": t2,
    "projMatrix": proj.getMatrix(),
    "cameraPosition": cam_position,
    "lightPosition": lightPosition,
    "texture": image,
}

start = time.time()

pipeline.draw(vertices, triangles, data)

end = time.time()
print(end - start)

import matplotlib.pyplot as plt

imgplot = plt.imshow(pipeline.image)
plt.show()
