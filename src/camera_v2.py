from numpy import array, cross
from numpy.linalg import norm

def camera_v2_mat(eye, target, up):
    lookAt = target - eye
    lookAt = lookAt / norm(lookAt)
    right = cross(lookAt, up)
    right = right / norm(right)
    a_up = cross(lookAt, right)
    a_up = a_up / norm(a_up)

    meye = -eye

    return array(
        [
            [*right, right.dot(meye)],
            [*a_up, a_up.dot(meye)],
            [*lookAt, lookAt.dot(meye)],
            [0, 0, 0, 1],
        ]
    )
