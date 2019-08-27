import vtk
import vmi
import numpy as np
import numpy.random.common
import numpy.random.bounded_integers
import numpy.random.entropy


class CS4x4:
    def __init__(self, other=None, origin=None, axis0=None, axis1=None, axis2=None):
        self._axis3x3 = np.identity(3)
        self._origin3 = np.zeros(3)
        if other is not None:
            self.ary4x4(other.ary4x4())
        if origin is not None:
            self.origin(origin)
        if axis0 is not None:
            self.axis(0, axis0)
        if axis1 is not None:
            self.axis(1, axis1)
        if axis2 is not None:
            self.axis(2, axis2)

    def __setstate__(self, s):
        self.__init__()
        self.__dict__.update(s)
        s = self.__dict__

    def __getstate__(self):
        s = self.__dict__.copy()
        for kw in []:
            if kw in s:
                del s[kw]
        return s

    def __repr__(self):
        return self.ary4x4().__repr__()

    def copy(self):
        cs = CS4x4()
        cs._axis3x3 = self._axis3x3.copy()
        cs._origin3 = self._origin3.copy()
        return cs

    def ary4x4(self, arg=None):
        if arg is not None:
            if np.linalg.matrix_rank(arg) < 3:
                raise np.linalg.LinAlgError('矩阵非满秩')
            else:
                self._axis3x3 = np.hsplit(arg, (3, 4))[0][:3]
                self._origin3 = arg[3][:3]
        return np.hstack((np.vstack((self._axis3x3, self._origin3)), ([0], [0], [0], [1])))

    def ary4x4inv(self):
        return np.linalg.inv(self.ary4x4())

    def mat4x4(self):
        return tomat4x4(self.ary4x4())

    def mat4x4inv(self):
        return tomat4x4(self.ary4x4inv())

    def inv(self):
        cs = CS4x4()
        cs.ary4x4(self.ary4x4inv())
        return cs

    def axis(self, i, arg=None):
        if arg is not None:
            t = np.array(self._axis3x3)
            t[i] = np.array(arg[:3])

            if np.linalg.matrix_rank(t) < 3:
                raise np.linalg.LinAlgError('矩阵非满秩')
            self._axis3x3[i] = np.array(arg)

        return self._axis3x3[i]

    def orthogonalize(self, args):
        for i in args:
            self.axis(i, np.cross(self.axis((i + 1) % 3), self.axis((i + 2) % 3)))

    def normalize(self, args=None):
        if args is None:
            args = [0, 1, 2]
        for i in args:
            self.axis(i, self.axis(i) / np.linalg.norm(self.axis(i)))

    def origin(self, arg=None):
        if arg is not None:
            self._origin3 = np.array(arg[:3])
        return self._origin3

    def mpt(self, pt, origin=None, other=None):
        """
        mpt([1,2,0], other): 点pt经self变换/点pt从self坐标系到other坐标系变换
        """
        origin_ = self.origin()
        if origin is not None:
            self.origin(origin)

        pt = np.append(np.array(pt[:3]), 1)
        pt = pt @ self.ary4x4()
        if other is not None:
            pt = pt @ other.ary4x4inv()

        if origin is not None:
            self.origin(origin_)
        return pt[:3]

    def mvt(self, vt, other=None):
        """
        mvt([1,2,0], other): 向量vt经self变换/向量vt从self坐标系到other坐标系变换
        """
        vt = np.append(np.array(vt[:3]), 0)
        vt = vt @ self.ary4x4()
        if other is not None:
            vt = vt @ other.ary4x4inv()
        return vt[:3]

    def mcs(self, cs):
        """
        mcs(CS4x4()): 坐标系cs经self变换/cs变换经self变换
        """
        cs = cs.ary4x4() @ self.ary4x4()
        return cs

    def translate(self, vt):
        mat = np.array([[1, 0, 0, vt[0]],
                        [0, 1, 0, vt[1]],
                        [0, 0, 1, vt[2]],
                        [0, 0, 0, 1]])
        self.ary4x4(self.ary4x4() @ mat)
        return self

    def rotate(self, angle, axis, origin=None):
        """
        https://en.wikipedia.org/wiki/Rotation_matrix#In_three_dimensions
        """
        axis = np.array(axis[:3])
        if np.linalg.norm(axis) == 0:
            raise np.linalg.LinAlgError('旋转轴向错误')

        angle = np.radians(angle)

        mat = np.cos(angle) * np.identity(3) + np.sin(angle) * np.array(
            [[0, axis[2], -axis[1]],
             [-axis[2], 0, axis[0]],
             [axis[1], -axis[0], 0]]) + (1 - np.cos(angle)) * np.outer(axis, axis)
        mat = np.hstack((np.vstack((mat, [0, 0, 0])), ([0], [0], [0], [1])))

        if origin is None:
            self.ary4x4(self.ary4x4() @ mat)
        else:
            origin = np.array(origin[:3])
            self.translate(-origin)
            self.ary4x4(self.ary4x4() @ mat)
            self.translate(origin)
        return self

    def reflect(self, normal, origin=None):
        """
        https://en.wikipedia.org/wiki/Reflection_(mathematics)#Reflection_through_a_hyperplane_in_n_dimensions
        """
        normal = np.array(normal[:3])
        if np.linalg.norm(normal) == 0:
            raise np.linalg.LinAlgError('反射法向错误')

        mat = np.identity(3) - 2 / np.linalg.norm(normal) ** 2 * np.outer(normal, normal)
        mat = np.hstack((np.vstack((mat, [0, 0, 0])), ([0], [0], [0], [1])))

        if origin is None:
            self.ary4x4(self.ary4x4() @ mat)
        else:
            origin = np.array(origin[:3])
            self.translate(-origin)
            self.ary4x4(self.ary4x4() @ mat)
            self.translate(origin)
        return self

    def scale(self, factor, origin=None):
        mat = np.identity(3) * np.array(factor[:3])
        mat = np.hstack((np.vstack((mat, [0, 0, 0])), ([0], [0], [0], [1])))

        if origin is None:
            self.ary4x4(self.ary4x4() @ mat)
        else:
            origin = np.array(origin[:3])
            self.translate(-origin)
            self.ary4x4(self.ary4x4() @ mat)
            self.translate(origin)
        return self


def toary4x4(arg):
    array = None
    if isinstance(arg, vtk.vtkTransform):
        arg = arg.GetMatrix()
    if isinstance(arg, vtk.vtkMatrix4x4):
        array = np.zeros((4, 4))
        for j in range(4):
            for i in range(4):
                array[i, j] = arg.GetElement(j, i)
    return array


def tomat4x4(arg):
    matrix = None
    if isinstance(arg, np.ndarray) and arg.shape == (4, 4):
        matrix = vtk.vtkMatrix4x4()
        for j in range(4):
            for i in range(4):
                matrix.SetElement(j, i, arg[i, j])
    return matrix


def add3x(scalars, vectors, origin=(0, 0, 0)):
    aa = [*origin]
    n = min(len(scalars), len(vectors))
    for j in range(n):
        for i in range(3):
            aa[i] += scalars[j] * vectors[j][i]
    return aa


def trsfLandmark(pts0, pts1, mode='rigidbody'):
    if len(pts0) > 2 and len(pts1) > 2:
        pts = [vtk.vtkPoints(), vtk.vtkPoints()]
        for pt in pts0:
            pts[0].InsertNextPoint(pt)
        for pt in pts1:
            pts[1].InsertNextPoint(pt)

        modes = {'rigidbody': vtk.VTK_LANDMARK_RIGIDBODY,
                 'similarity': vtk.VTK_LANDMARK_SIMILARITY,
                 'affine': vtk.VTK_LANDMARK_AFFINE}
        ts = vtk.vtkLandmarkTransform()
        ts.SetSourceLandmarks(pts[0])
        ts.SetTargetLandmarks(pts[1])
        if mode in modes:
            ts.SetMode(modes[mode])
        else:
            ts.SetModeToRigidBody()
        ts.Update()
        return ts


def ptOnPlane(pt, origin, normal):
    pt, origin, normal = np.array(pt), np.array(origin), np.array(normal)
    return pt - normal * np.dot(pt - origin, normal)


def vtOnPlane(vt, normal):
    vt, normal = np.array(vt), np.array(normal)
    n2 = np.dot(normal, normal)
    n2 = n2 if n2 != 0 else 1
    t = np.dot(vt, normal)
    return vt - t * normal / n2


def vtOnVector(vt, vector):
    dot = np.dot(vector, vector)
    if dot == 0:
        return [0, 0, 0]

    dot = np.dot(vt, vector) / dot
    return [dot * vector[i] for i in range(3)]
