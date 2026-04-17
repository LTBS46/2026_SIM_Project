from numpy.linalg import norm
from time import time
from PIL import Image
from numpy import asarray, array, dot, ones
from copy import deepcopy
from math import sqrt
from load_entries import load_entries
from matplotlib.pyplot import imshow, show, title, subplot
from graphicPipeline import GraphicPipeline
from projection import Projection
from orthographic_projection import OrthographicProjection
from camera_v2 import camera_v2_mat
from sys import argv
from json import load
from os.path import abspath, dirname, join

config_opt = None

if len(argv) > 1:
    config_opt = argv[1]
else:
    config_opt = "../data/basic.json"

config_file = abspath(config_opt)
config = None

with open(config_file, "r") as f:
    config = load(f)
config_path = dirname(config_file)

e_cnt = len(config["elements"]) 

entries = [None] * e_cnt
textures = [None] * e_cnt
offset = [None] * e_cnt

white = ones((1, 1, 3)) * 255

for idx, element in enumerate(config["elements"]):
    assert "object" in element, "Each element must have an 'object' field"
    entries[idx] = join(config_path, element["object"])
    offset[idx] = array(element.get("offset", [0, 0, 0]))

    if "texture" in element:
        textures[idx] = asarray(Image.open(join(config_path, element["texture"])))
    else:
        textures[idx] = white

# le premier ply aura l'id 0, le second l'id 1, etc...
# le tid (numero de texture) est le même
vertices, triangles = load_entries(entries, offset)



width = 1280
height = 720

pipeline = GraphicPipeline(width, height)

cam_position = array([3, 3, 1.6])
target = array([0, 0, 0])
d_up = array([0, 0, 1])
light_target = target

# +front -back 
# +left ear -right ear
# +up -down

lightPosition = array([1.1, -1.1, 1.1])
# Pour mettre la lumière au-dessus de la scène : 
# lightPosition = array([0.01, 0.01, 1.5])

mat_view = camera_v2_mat(cam_position, target, d_up)
mat_shadow = camera_v2_mat(lightPosition, light_target, d_up)

nearPlane = 0.1
farPlane = 10.0
fov = 1.91986
aspectRatio = width / height

proj = Projection(nearPlane, farPlane, fov, aspectRatio)



ltn = norm(light_target - lightPosition)
ltr = (light_target - lightPosition) / ltn

max_d = 0.0
for vertice in vertices:
    vert = vertice[:3]
    vtn = norm(vert)
    vtr = vert / vtn
    ndi = vert - light_target
    nd = sqrt(sum(ndi * ndi))
    ndti = abs(dot(ltr, vtr))
    ndt = sqrt(1 - (ndti * ndti))
    nd *= ndt
    if nd > max_d:
        max_d = nd
        
proj_shadow = OrthographicProjection(-nearPlane, -farPlane, -max_d, max_d, max_d, -max_d)

# load and show an image with Pillow
# Open the image form working directory

data_shadow = {
    "viewMatrix": mat_shadow,
    "projMatrix": proj_shadow.getMatrix(),
    "cameraPosition": lightPosition,
    "lightPosition": lightPosition,
    "is_shadow": True,
}

data = {
    "viewMatrix": mat_view,
    "projMatrix": proj.getMatrix(),
    "cameraPosition": cam_position,
    "lightPosition": lightPosition,
    "textures": textures,
    "shadowView": mat_shadow,
    "shadowProj": proj_shadow.getMatrix()
}


# Vue shadow
shadow_size = 1080 # 1080
pipeline2 = GraphicPipeline(shadow_size, shadow_size)
print("Making the shadow map")
start = time()
pipeline2.draw(vertices, triangles, data_shadow)
end = time()
print("time: ", end - start)
image2 = -deepcopy(pipeline2.image)

# Prep rendu final
data["shadowMap"] = image2
pipeline4 = GraphicPipeline(width, height)
print("Making the final render")
start = time()

# Rendu final
pipeline4.draw(vertices, triangles, data)

# Collection rendu final
end = time()
print("time: ", end - start)
image4 = deepcopy(pipeline4.image)

###############################################################################
# Affichage
###############################################################################
# Affichage côte à côte
subplot(1, 2, 2)
imshow(image2)
title("Depth map")
subplot(1, 2, 1)
print("Showing the render")
imshow(image4)
title("Rendu")

Image.fromarray((image4 * 255).astype("uint8")).save("render.png")

show()