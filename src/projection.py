import numpy as np


class Projection:
    def __init__(self, near, far, fov, aspectRatio):
        self.nearPlane = near
        self.farPlane = far
        self.fov = fov
        self.aspectRatio = aspectRatio

    def getMatrix(self):
        f = self.farPlane
        n = self.nearPlane
        s = 1 / np.tan(self.fov / 2)
        fn = f / (f - n)
        perspective = np.array(
            [
                [s / self.aspectRatio, 0, 0, 0],
                [0, s, 0, 0],
                [0, 0, fn, -n * fn],
                [0, 0, 1, 0],
            ]
        )

        return perspective
