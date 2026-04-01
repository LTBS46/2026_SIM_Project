import numpy as np

# Source : https://www.scratchapixel.com/lessons/3d-basic-rendering/perspective-and-orthographic-projection-matrix/orthographic-projection-matrix.html

class OrthographicProjection:
    def __init__(self, near, far, left, right, top, bottom):
        self.nearPlane = near
        self.farPlane = far
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

    def getMatrix(self):
        f = self.farPlane
        n = self.nearPlane
        l = self.left
        r = self.right
        t = self.top
        b = self.bottom
        perspective = np.array(
            [
                [2 / (r - l), 0, 0, - ((r + l) / (r - l))],
                [0, 2 / (t - b), 0, - ((t + b) / (t - b))],
                [0, 0, -2 / (f - n), - ((f + n) / (f - n))],
                [0, 0, 0, 1],
            ]
        )

        return perspective
