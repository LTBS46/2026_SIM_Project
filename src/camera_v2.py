from numpy import array, cross
from numpy.linalg import norm

def camera_v2(eye, target, up):
    lookAt = target - eye
    lookAt = lookAt / norm(lookAt)
    right = cross(lookAt, up)
    right = right / norm(right)
    a_up = cross(lookAt, right)
    a_up = a_up / norm(a_up)

    return lookAt, right, a_up