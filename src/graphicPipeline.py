import numpy as np

STAGE0_FRAGMENT_SIZE = 9
STAGE1_FRAGMENT_SIZE = 19

def sample(texture, u, v):
    u = np.clip(u, 0.0, 0.9999)
    v = np.clip(v, 0.0, 0.9999)

    u = int(u * (texture.shape[0] - 1))
    v = int((1 - v) * (texture.shape[1] - 1))

    return texture[u, v] / 255.0


def clip_z0(v0, v1, v2): # none to clip
    return np.array([v0, v1, v2]), np.array([[0, 1, 2]])

def clip_z1(v0, v1, v2): # v0 to clip
    raise NotImplementedError("clip_z1 is not implemented yet")
    nv0 = ...
    nv1 = ...

    return np.array([nv, v1, v2]), np.array([[0, 1, 2]])

def clip_z2(v0, v1, v2): # v0 and v1 to clip
    raise NotImplementedError("clip_z2 is not implemented yet")
    pass

def clip_z3(v0, v1, v2): # clip all
    return np.array([]).reshape(0, STAGE1_FRAGMENT_SIZE), np.array([]).reshape(0, 3)

def clip_z(v0, v1, v2):
    b0 = v0[2] < 0
    b1 = v1[2] < 0
    b2 = v2[2] < 0
    if b0:
        print("v0 to clip")
    elif b1:
        print("v1 to clip")
    elif b2:
        print("v2 to clip")
    else:
        return clip_z0(v0, v1, v2)

    match (b0, b1, b2):
        case (False, False, False): # None to clip
            return clip_z0(v0, v1, v2)
        case (True, False, False): # v0 to clip
            return clip_z1(v0, v1, v2)
        case (False, True, False): # v1 to clip
            return clip_z1(v1, v2, v0)
        case (False, False, True): # v2 to clip
            return clip_z1(v2, v0, v1)
        case (True, True, False): # v0 and v1 to clip
            return clip_z2(v0, v1, v2)
        case (True, False, True): # v0 and v2 to clip
            return clip_z2(v2, v0, v1)
        case (False, True, True): # v1 and v2 to clip
            return clip_z2(v1, v2, v0)
        case (True, True, True): # all to clip
            return clip_z3(v0, v1, v2)
        case a:
            raise ValueError("Invalid case in clip_z:" + str(a))

class Fragment:
    def __init__(self, x: int, y: int, depth: float, interpolated_data):
        self.x = x
        self.y = y
        self.depth = depth
        self.interpolated_data = interpolated_data
        self.output = []


def edgeSide(p, v0, v1):
    return (p[0] - v0[0]) * (v1[1] - v0[1]) - (p[1] - v0[1]) * (v1[0] - v0[0])

def remove_dup(vert, tri):
    output = {}
    idx = 0

    tt = {}

    for i, e in enumerate(vert):
        e = (*e,)
        if e in output:
            tt[i] = output[e]
        else:
            output[e] = idx
            tt[i] = idx
            idx += 1

    newVertices = np.zeros((idx, STAGE1_FRAGMENT_SIZE))

    for k, v in output.items():
        newVertices[v] = [*k]
    
    for i in range(len(tri)):
        tri[i,:] = [tt[tri[i, 0]], tt[tri[i, 1]], tt[tri[i, 2]]]

    return newVertices, tri

class GraphicPipeline:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.image = np.zeros((height, width, 3))
        self.depthBuffer = np.ones((height, width))

    def VertexShader(self, vertex, data):
        outputVertex = np.zeros((STAGE1_FRAGMENT_SIZE))

        vec = data["projMatrix"] @ data["viewMatrix"] @ [*vertex[0:3], 1.0]

        outputVertex[0:3] = vec[0:3]

        outputVertex[3:6] = vertex[3:6]

        outputVertex[6:9] = data["cameraPosition"][0:3] - vertex[0:3]

        outputVertex[9:12] = data["lightPosition"][0:3] - vertex[0:3]

        outputVertex[12:14] = vertex[6:8]

        outputVertex[14] = vec[3]

        outputVertex[15:18] = vertex[0:3]

        outputVertex[18] = vertex[8]

        return outputVertex

    def Rasterizer(self, v0, v1, v2):
        fragments = []

        # culling back face
        area = edgeSide(v0, v1, v2)
        if area < 0:
            return fragments

        # AABBox computation
        # compute vertex coordinates in screen space
        size_pair = np.array([self.width, self.height])

        v_images = (np.array([v0, v1, v2])[:, 0:2] + 1) / 2.0 * size_pair

        # compute the two point forming the AABBox
        max_image = size_pair - 1
        min_image = np.array([0.0, 0.0])

        A = np.min(v_images, axis=0)
        B = np.max(v_images, axis=0)

        A = np.max(np.array([A, min_image]), axis=0).astype(int)
        B = np.min(np.array([B, max_image]), axis=0).astype(int) + 1

        # for each pixel in the bounding box
        for j in range(A[1], B[1]):
            for i in range(A[0], B[0]):
                x = (i + 0.5) / self.width * 2.0 - 1
                y = (j + 0.5) / self.height * 2.0 - 1

                p = np.array([x, y])

                area0 = edgeSide(p, v0, v1)
                area1 = edgeSide(p, v1, v2)
                area2 = edgeSide(p, v2, v0)

                # test if p is inside the triangle
                if area0 >= 0 and area1 >= 0 and area2 >= 0:

                    # Computing 2d barricentric coordinates
                    lambda0 = area1 / area
                    lambda1 = area2 / area
                    lambda2 = area0 / area

                    z = lambda0 * v0[2] + lambda1 * v1[2] + lambda2 * v2[2]


                    one_over_w = lambda0 * 1/v0[14] + lambda1 * 1/v1[14] + lambda2 * 1/v2[14]
                    w = 1/one_over_w

                    # interpolating
                    interpolated_data = (
                        v0[3:] * lambda0/v0[14] + v1[3:] * lambda1/v1[14] + v2[3:] * lambda2/v2[14]
                    )*w

                    # Emiting Fragment
                    fragments.append(Fragment(i, j, z, interpolated_data))

        return fragments

    def fragmentShader(self, fragment: Fragment, data: dict):
        N = fragment.interpolated_data[0:3]
        N = N / np.linalg.norm(N)
        V = fragment.interpolated_data[3:6]
        V = V / np.linalg.norm(V)
        L = fragment.interpolated_data[6:9]
        L = L / np.linalg.norm(L)

        og_vertice = [*fragment.interpolated_data[12:15], 1]

        vec = data["shadowProj"] @ data["shadowView"] @ og_vertice
        vec /= vec[3]

        o_old_d = -vec[2]

        vec = (vec + 1) / 2

        # o_old_d = vec[2]

        shadow_tex = sample(data["shadowMap"], vec[1], 1-vec[0]) * 255
        shadow_tex = shadow_tex[0]

        if data.get("flag") == "fetch_shadow":
            fragment.output = np.array([shadow_tex, shadow_tex, shadow_tex])
            return
        elif data.get("flag") == "calc_shadow":
            fragment.output = np.array([o_old_d, o_old_d, o_old_d])
            return

        intensity = 1.0

        bias = 0.02

        tid = round(fragment.interpolated_data[15])


        if shadow_tex > o_old_d + bias:
            intensity = 0.5
            """ fragment.output = np.array([1.0,0,0])
            if tid == 1 and fragment.y > 500:
                print(f"{shadow_tex=}, {o_old_d=}")            
            return """


        R = 2 * np.dot(L, N) * N - L

        ambient = 1.0
        diffuse = max(np.dot(N, L), 0)
        specular = np.power(max(np.dot(R, V), 0.0), 64)

        ka = 0.1
        kd = 0.9
        ks = 0.3
        phong = ka * ambient + (kd * diffuse + ks * specular) * intensity
        phong = np.ceil(phong * 4 + 1) / 6.0

        tex = data["textures"][tid]
        texture = sample(
            tex,
            1 - fragment.interpolated_data[10],
            1 - fragment.interpolated_data[9],
        )

        color = np.array([phong, phong, phong]) * texture

        fragment.output = color

    def draw(self, vertices, triangles, data: dict):
        # Calling vertex shader
        newVertices = np.zeros((vertices.shape[0], STAGE1_FRAGMENT_SIZE))

        for i in range(vertices.shape[0]):
            newVertices[i] = self.VertexShader(vertices[i], data)

        if not data.get("is_shadow", False): # probably do not work on orthographic
            nnV, nnT = [None] *triangles.shape[0], [None] *triangles.shape[0]
            vc = 0

            for i in range(triangles.shape[0]):
                t = triangles[i]
                nnV[i], nnT[i] = clip_z(newVertices[t[0]],newVertices[t[1]],newVertices[t[2]])
                nnT[i] += vc
                vc += len(nnV[i])

            newVertices = np.concatenate(nnV)
            triangles = np.concatenate(nnT)

            newVertices, triangles = remove_dup(newVertices, triangles)

        for i in range(newVertices.shape[0]):
            newVertices[i, 0:3] = newVertices[i, 0:3] / newVertices[i, 14]

        newVertices, triangles = remove_dup(newVertices, triangles)

        fragments = []
        # Calling Rasterizer
        for i in triangles:
            fragments.extend(
                self.Rasterizer(
                    newVertices[i[0]],
                    newVertices[i[1]],
                    newVertices[i[2]],
                )
            )

        if data.get("is_shadow") is True:
            for f in fragments:
                # depth test
                if self.depthBuffer[f.y][f.x] > f.depth:
                    self.depthBuffer[f.y][f.x] = f.depth
                    self.image[f.y][f.x] = f.depth
        else:
            for f in fragments:
                # depth test
                if self.depthBuffer[f.y][f.x] > f.depth:
                    self.depthBuffer[f.y][f.x] = f.depth
                    self.fragmentShader(f, data)
                    self.image[f.y][f.x] = f.output
