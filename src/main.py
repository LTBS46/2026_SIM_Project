import numpy as np
from numpy.linalg import norm
width = 1280
height = 720

import time

start = time.time()


from graphicPipeline import GraphicPipeline


pipeline = GraphicPipeline(width, height)


from camera import Camera
from projection import Projection
from camera_v2 import camera_v2

position = np.array([1.1, 1.1, 1.1])

lookAt, right, up = camera_v2(position, np.array([0, 0, 0]), np.array([0, 0, 1]))

print(f"{lookAt = }")
print(f"{up = }")
print(f"{right = }")

cam = Camera(position, lookAt, up, right)

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
    "viewMatrix": cam.getMatrix(),
    "projMatrix": proj.getMatrix(),
    "cameraPosition": position,
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
