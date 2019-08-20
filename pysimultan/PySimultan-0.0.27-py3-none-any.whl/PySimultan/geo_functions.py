# -*- coding: utf-8 -*-

import numpy as np
import numpy.matlib
import itertools
from time import time
from numba import jit  # vectorize, cuda
import numba
import trimesh


def magnitude(vec):  # vector magnitude
    return np.sqrt(vec[0] ** 2 + vec[1] ** 2 + vec[2] ** 2)


def __default_set_handling(self, attr_name, value):
    default_notification = True

    if isinstance(value, tuple):
        setattr(self, '_' + attr_name, value[0])
        notify_observers = default_notification
        if value.__len__() > 1:
            if 'notify_observers' in value[1]:
                notify_observers = value[1]
            else:
                notify_observers = default_notification
    else:
        self._Layers = value
        notify_observers = default_notification

    if notify_observers:
        for callback in self._observers:
            print(attr_name + '_changed')
            callback(ChangedAttribute=attr_name)


def collinear_check(p0, p1, p2, eps=1e-12):
    """Check if three points are collinear
    :param p0:      coordinates of the first point [1 x 3 np.array]
    :param p1:      coordinates of the second point [1 x 3 np.array]
    :param p2:      coordinates of the third point [1 x 3 np.array]
    :param eps:     tolerance
    :return:        true if collinear, false if not collinear
    """

    return abs(np.linalg.norm(cross(p0-p1, p2-p1))) < eps


def polygon_area_3d(poly_coord):
    """Calculate Area of a 3D polygon

    Example: area of a simple 3D square

    poly = [10, 30, 20;
            20, 30, 20;
            20, 40, 20;
            10, 40, 20]

    polygon_area_3d(poly)
    ans =
     100

    :param poly_coord:      N - by - 3 array of vertex coordinates.The resulting area is positive.
    :return:                Area of the polygon [m²]
    """

    # put the first vertex at origin (reducing computation errors for polygons
    # far from origin)
    v0 = poly_coord[0, :]
    poly_coord = poly_coord - v0

    # indices of next vertices
    n = poly_coord.shape[0]
    i_next = np.append(np.arange(1, n), 0)

    # compute cross-product of each elementary triangle formed by origin and
    # two consecutive vertices
    cp = np.cross(poly_coord, poly_coord[i_next, :], axis=1)

    # choose one of the triangles as reference for the normal direction
    vn = np.linalg.norm(cp, axis=1)

    ind = np.argmax(vn)
    # tmp = vn[ind]
    cp_ref = cp[ind, :]

    # compute the sign of the area of each triangle
    # (need to compute the sign explicitly, as the norm of the cross product
    # does not keep orientation within supporting plane)

    cp_ref_mat = np.matlib.repmat(cp_ref, n, 1)
    sign_i = np.sign(np.sum(np.conj(cp) * cp_ref_mat, 1))

    # compute area of each triangle, using sign correction
    area_i = np.linalg.norm(cp, axis=1) * sign_i

    # sum up individual triangles area
    area = sum(area_i) / 2

    return area


def unit_normal(a, b, c):
    """Calculate the unit normal vector of plane defined by points a, b, and c

    collinear check is done

    :param a:       coordinates of the first point [1 x 3 array]
    :param b:       coordinates of the second point [1 x 3 array]
    :param c:       coordinates of the third point [1 x 3 array]
    :return:        unit normal [1 x 3 array]
    """
    # unit normal vector of plane defined by points a, b, and c

    if collinear_check(a, b, c):
        raise ValueError('Points are collinear')

    x = np.linalg.det([[1, a[1], a[2]],
             [1, b[1], b[2]],
             [1, c[1], c[2]]])
    y = np.linalg.det([[a[0], 1, a[2]],
             [b[0], 1, b[2]],
             [c[0], 1, c[2]]])
    z = np.linalg.det([[a[0], a[1], 1],
             [b[0], b[1], 1],
             [c[0], c[1], 1]])
    magnitude = (x**2 + y**2 + z**2)**.5
    return np.array((x/magnitude, y/magnitude, z/magnitude))


def cross(a, b):
    # cross product of vectors a and b
    x = a[1] * b[2] - a[2] * b[1]
    y = a[2] * b[0] - a[0] * b[2]
    z = a[0] * b[1] - a[1] * b[0]
    return np.array((x, y, z))


def convert_to_local(points):
    """Convert the 3D polygon to a 2D polygon

    :param points:          (n x 3) np.array with the polygon coordinates
    :return:
        local_coords:       (n x 2) np.array 2D Coordinates of the polygon
        trans:              Transformation - object
    """

    indx1 = 0
    indx2 = 1
    indx3 = 2

    # check if the first three points are collinear:
    collinear = collinear_check(points[indx1, :], points[indx2, :], points[indx3, :])
    while collinear and points.__len__() > 3:
        # if collinear
        indx1 += 0
        indx2 += 1
        indx3 += 2
        collinear = collinear_check(points[indx1, :], points[indx2, :], points[indx3, :])

    d = points[indx1, :]                # local origin

    # translate point 1 in origin:
    transl_points = points - d

    u = transl_points[indx2, :]           # local X axis
    u = u / np.linalg.norm(u)       #

    w = cross(u, transl_points[indx3, :])
    w = w / np.linalg.norm(w)

    v = cross(w, u)

    trans = Transformation(u, v, w, -d)

    # add column of ones to coordinates:
    points_0 = np.c_[points, np.ones(points.shape[0])]

    local_coords = np.matmul(points_0, trans.return_rotation_matrix())
    # remove last column:
    local_coords = local_coords[:, :-1]

    # remove column where all entries are zero:
    if any((local_coords < 1e-5).all(axis=0)):
        local_coords = local_coords[:, ~(local_coords < 1e-5).all(axis=0)]
    else:
        raise ValueError('the polygon could not be converted to 2d')

    # test inverse transformation:
    convert_to_global(trans.transformation_mat, local_coords)

    if not(local_coords.shape[1] == 2):
        raise ValueError('the polygon could not be converted to 2d. Shape is incorrect')

    return local_coords, trans


def convert_to_global(trans_mat, local_coords):
    """Convert local coordinates to global coordinates

    :param trans_mat:               transformation matrix to convert global to local (4 x 4) numpy array
    :param local_coords:            local coordinates of the points (n x 2) or (2 x 3) numpy array
    :return:                        global coordinates (n x 3) numpy array
    """

    # add column of zeros to coordinates (z-koordinate):
    if local_coords.shape[1] == 2:
        local_coords = np.c_[local_coords, np.zeros(local_coords.shape[0])]
    # add column of ones to coordinates:
    points_0 = np.c_[local_coords, np.ones(local_coords.shape[0])]

    return np.matmul(points_0, np.linalg.inv(trans_mat))[:,0:3]


@jit(nopython=True)
def in_polygon(points, poly):
    """Function to test if points lie in polygon:

    :param points:      y-coordinates of the points [n x 2] numpy array
    :param poly:        x/y-coordinates of the points [n x 2] numpy array
    :return:            true if points lie inside polygon, false otherwise [n x 1] numpy array
    """

    # check if polygon is closed:

    if np.any(poly[-1, :] != poly[0, :]):
        # if not closed append first point:
        add = np.expand_dims(poly[0, :], axis=0)
        poly0 = np.vstack((poly, add))
        # poly0 = poly
    else:
        # poly = poly
        poly0 = poly
    # poly0 = np.vstack((poly, poly[0, 0:3]))

    num_points = points.shape[0]
    inside = np.zeros(num_points, dtype=numba.boolean)

    # test if points are located inside or outside of min/max of points:
    test_points = (points[:, 0] < np.max(poly0[:, 0])) & \
                  (points[:, 0] > np.min(poly0[:, 0])) & \
                  (points[:, 1] < np.max(poly0[:, 1])) & \
                  (points[:, 1] > np.min(poly0[:, 1]))

    number_of_testpoints = numpy.sum(test_points)

    x = points[test_points, 0]
    y = points[test_points, 1]

    n = len(poly0)

    p1x, p1y = poly0[0]

    is_in = np.zeros(number_of_testpoints, dtype=numba.boolean)

    for i in range(n):

        p2x = poly0[i, 0]
        p2y = poly0[i, 1]

        y_greater = y > np.minimum(p1y, p2y)
        y_less = y <= np.maximum(p1y, p2y)
        x_less = x <= np.maximum(p1x, p2x)

        not_equal = not (p1y == p2y)

        if not not_equal:
            statement = np.ones(number_of_testpoints, dtype=numba.boolean) & (p1x == p2x)
        else:
            xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
            statement = (np.ones(number_of_testpoints, dtype=numba.boolean) & (p1x == p2x)) | (x <= xints)

        cond_true = y_greater & y_less & not_equal & x_less & statement
        if np.any(cond_true):
            is_in[cond_true] = np.logical_not(is_in[cond_true])
        p1x = p2x
        p1y = p2y
    inside[test_points] = is_in

    return inside


@jit(nopython=True, parallel=True)
def inpolygon_multiple(points, poly):
    print('startet')
    for cur_poly in poly:
        in_polygon(points, cur_poly)
    print('finished')


def create_volume_mesh_from_faces(zone):

    vertices = []
    faces = []

    first_vertex_id = 0

    for face in zone.Faces:
        num_nodes = face._Triangulation['vertices3D'].shape[0]
        if vertices.__len__() == 0:
            vertices = face._Triangulation['vertices3D']
            faces = face._Triangulation['triangles']
            first_vertex_id += num_nodes
        else:
            vertices = np.vstack((vertices, face._Triangulation['vertices3D']))
            faces = np.vstack((faces, face._Triangulation['triangles'] + first_vertex_id))
            first_vertex_id += num_nodes

    vertices, u = np.unique(vertices, axis=0, return_inverse=True)
    faces = chagem(faces, np.arange(faces.max()), u)

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    return mesh


def chagem(array, old_ind, new_ind):
    index = np.digitize(array.ravel(), old_ind, right=True)
    return new_ind[index].reshape(array.shape)


class Transformation:

    ZeroTMat = np.eye(4, dtype=float)

    def __init__(self, u, v, w, d):

        self.RotMat = np.transpose(np.array((u,
                                             v,
                                             w))
                                   )
        self.d = d

        self.transformation_mat = self.return_rotation_matrix()

    def return_rotation_matrix(self):

        rotation_mat = np.copy(self.ZeroTMat)
        rotation_mat[0:3, 0:3] = self.RotMat

        translation_mat = np.copy(self.ZeroTMat)
        translation_mat[3, 0:3] = self.d

        transformation_mat = np.matmul(translation_mat, rotation_mat)

        return transformation_mat

    def transform(self, points, dimension=2):

        points_0 = np.c_[points, np.ones(points.shape[0])]
        local_coords = np.matmul(points_0, self.transformation_mat)
        # remove last column:
        local_coords = local_coords[:, :-1]

        if dimension == 2:
            # remove column where all entries are zero:
            if any((local_coords < 1e-3).all(axis=0)):
                local_coords = local_coords[:, ~(local_coords < 1e-3).all(axis=0)]
            else:
                raise ValueError('the polygon could not be converted to 2d')

            if not (local_coords.shape[1] == 2):
                raise ValueError('the polygon could not be converted to 2d. Shape is incorrect')

        return local_coords


class Vector(object):
    new_vec_id = itertools.count(0)

    def __init__(self, x, y, z):
        self.id = next(self.new_vec_id)
        self.x = x
        self.y = y
        self.z = z

    def dot(self, b):  # vector dot product
        return self.x*b.x + self.y*b.y + self.z*b.z

    def cross(self, b):  # vector cross product
        return self.y*b.z-self.z*b.y, self.z*b.x-self.x*b.z, self.x*b.y-self.y*b.x

    def magnitude(self):  # vector magnitude
        return np.sqrt(self.x**2+self.y**2+self.z**2)

    def normal(self):  # compute a normalized (unit length) vector
        mag = self.magnitude()
        return Vector(self.x/mag, self.y/mag, self.z/mag)
        # Provide "overridden methods via the "__operation__" notation; allows you to do, for example, a+b, a-b, a*b

    def __add__(self, b):  # add another vector (b) to a given vector (self)
        return Vector(self.x + b.x, self.y+b.y, self.z+b.z)

    def __sub__(self, b):  # subtract another vector (b) from a given vector (self)
        return Vector(self.x-b.x, self.y-b.y, self.z-b.z)

    def __mul__(self, b):  # scalar multiplication of a given vector
        assert type(b) == float or type(b) == int
        return Vector(self.x*b, self.y*b, self.z*b)


class Plane:
    def __init__(self, point, normal):
        self.n = normal
        self.p = point
        # hessian normal form: A * x + B * y + C * z + D = 0
        # Hesse = [A B C D]
        d = - np.dot(self.p.location, self.n)
        self.Hesse = np.array([normal[0], normal[1], normal[2], d])


class Timer(object):
    """
    usage:

    with Timer('foo_stuff'):
    # do some foo
    # do some stuff
    """
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.tstart = time.time()

    def __exit__(self, type, value, traceback):
        if self.name:
            print('[%s]' % self.name,)
        print('Elapsed: %s' % (time.time() - self.tstart))


def print_status(*args, **kwargs):
    if args is not None:
        if args.__len__() == 1:
            m_str = args[0]
        elif args.__len__() > 1:
            m_str = ''.join(args)
        else:
            return
    else:
        return

    if kwargs is not None:
        if 'end' in kwargs:
            print(m_str, end=kwargs.get('end'))
        else:
            print(m_str)
    else:
        print(m_str)


if __name__ == '__main__':

    number_of_polys = 100

    polygon = np.array(([0.25, 0.25],
                        [0.25, 0.75],
                        [0.75, 0.75],
                        [0.75, 0.25]))

    polys = list()

    for i in range(number_of_polys):
        polys.append(polygon)

    #print('Area is: ', polygon_area_3d(polygon))

    # test in_polygon:
    # lenpoly = 4


    # lenpoly = 10
    # polygon = np.array([[np.sin(x) + 0.5, np.cos(x) + 0.5] for x in np.linspace(0, 2 * np.pi, lenpoly)[:-1]])

    # points = np.array(([0.10, 0.10],
    #                    [0.50, 0.50],
    #                    [0.30, 0.78],
    #                    [0.23, 0.78],
    #                    [0.26, 0.26]))

    # random points set of points to test
    N = 100000
    points = np.array((np.random.random(N), np.random.random(N))).transpose()

    start_time = time()
    print('startet')
    for i in range(number_of_polys):
        in_polygon(points, polygon)
    print('finished')
    print("Ray Tracing Elapsed time: " + str(time() - start_time))


    start_time = time()
    inpolygon_multiple(points, polys)
    print("Ray Tracing Elapsed time: " + str(time() - start_time))



