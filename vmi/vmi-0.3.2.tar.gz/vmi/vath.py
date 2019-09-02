from typing import Optional, List

import vtk
import vmi
import numpy as np
import numpy.random.common
import numpy.random.bounded_integers
import numpy.random.entropy

vmi.CS4x4 = None


class CS4x4:
    """
    坐标系，以4x4矩阵表示的局部坐标系或坐标变换
    """

    def __init__(self, axis0: Optional[np.ndarray] = None, axis1: Optional[np.ndarray] = None,
                 axis2: Optional[np.ndarray] = None, origin: Optional[np.ndarray] = None):
        """
        局部坐标系

        :param axis0: 3x1第一坐标轴，转为齐次坐标构成矩阵的第一行
        :param axis1: 3x1第二坐标轴，转为齐次坐标构成矩阵的第二行
        :param axis2: 3x1第三坐标轴，转为齐次坐标构成矩阵的第三行
        :param origin: 3x1坐标原点，转为齐次坐标构成矩阵的第四行
        """
        self._axis3x3 = np.identity(3)
        self._origin3 = np.zeros(3)
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

    def copy(self) -> vmi.CS4x4:
        """
        复制实例

        :return: vmi.CS4x4 - 具有相同矩阵的实例
        """
        cs = CS4x4()
        cs._axis3x3 = self._axis3x3.copy()
        cs._origin3 = self._origin3.copy()
        return cs

    def ary4x4(self, ary: Optional[np.ndarray] = None) -> np.ndarray:
        """
        返回当前矩阵，或设置新矩阵

        :param ary: 4x4新矩阵
        :return: np.ndarray - 当前矩阵
        """
        if ary is not None:
            self._origin3 = ary[3][:3]
        return np.hstack((np.vstack((self._axis3x3, self._origin3)), ([0], [0], [0], [1])))

    def ary4x4inv(self) -> np.ndarray:
        """返回当前矩阵的逆矩阵"""
        return np.linalg.inv(self.ary4x4())

    def vtkmat4x4(self, mat: vtk.vtkMatrix4x4 = None) -> vtk.vtkMatrix4x4:
        """返回当前矩阵的vtk矩阵，或设置新vtk矩阵"""
        if mat is not None:
            ary = np.zeros(4, 4)
            for j in range(4):
                for i in range(4):
                    ary[i, j] = mat.GetElement(j, i)

        ary = self.ary4x4()
        matrix = vtk.vtkMatrix4x4()
        for j in range(4):
            for i in range(4):
                matrix.SetElement(j, i, ary[i, j])
        return matrix

    def mat4x4inv(self) -> vtk.vtkMatrix4x4:
        """返回当前矩阵的vtkMatrix4x4逆矩阵"""
        ary = self.ary4x4inv()
        matrix = vtk.vtkMatrix4x4()
        for j in range(4):
            for i in range(4):
                matrix.SetElement(j, i, ary[i, j])
        return matrix

    def inv(self) -> vmi.CS4x4:
        """返回逆变换"""
        cs = CS4x4()
        cs.ary4x4(self.ary4x4inv())
        return cs

    def axis(self, i: int, arg: Optional[np.ndarray] = None) -> np.ndarray:
        """
        返回第i坐标轴，或设置新坐标轴
        :param i: 坐标轴次序
        :param arg: 3x1新坐标轴
        :return: 3x1当前第i坐标轴
        """
        if arg is not None:
            t = np.array(self._axis3x3)
            t[i] = np.array(arg[:3])
            self._axis3x3[i] = np.array(arg)

        return self._axis3x3[i]

    def origin(self, arg: Optional[np.ndarray] = None) -> np.ndarray:
        """
        返回坐标原点

        :param arg: 3x1新坐标原点
        :return: 3x1坐标原点
        """
        if arg is not None:
            self._origin3 = np.array(arg[:3])
        return self._origin3

    def orthogonalize(self, i_list: List[int]) -> None:
        """
        按照次序列表正交化坐标轴，例如i_list=[0, 2]表示先用z轴y轴正交化x轴，再用x轴y轴正交化z轴

        :param i_list: 坐标轴次序列表
        :return: None
        """
        for i in i_list:
            self.axis(i, np.cross(self.axis((i + 1) % 3), self.axis((i + 2) % 3)))

    def normalize(self, i_list: List[int]) -> None:
        """
        按照次序列表单位化坐标轴，例如i_list=[0, 2]表示将x轴z轴单位化

        :param i_list: 坐标轴次序列表
        :return: None
        """
        if i_list is None:
            i_list = [0, 1, 2]
        for i in i_list:
            self.axis(i, self.axis(i) / np.linalg.norm(self.axis(i)))

    def mpt(self, pt: np.ndarray, origin: Optional[np.ndarray] = None,
            other: Optional[vmi.CS4x4] = None) -> np.ndarray:
        """
        坐标系变换：点pt由当前坐标系变换到世界坐标系，如果设置了other则变换到other坐标系
        坐标变换：世界坐标系中的点pt经过当前变换得到新点，如果设置了origin则在此次计算中原点暂时设为origin

        :param pt: 3x1点坐标
        :param origin: 3x1坐标原点
        :param other: 坐标系
        :return: 变换后坐标
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

    def mvt(self, vt: Optional[np.ndarray], other: Optional[vmi.CS4x4] = None) -> np.ndarray:
        """
        坐标系变换：向量vt由当前坐标系变换到世界坐标系，如果设置了other则变换到other坐标系
        坐标变换：世界坐标系中的向量vt经过当前变换，获得新向量

        :param vt: 3x1向量
        :param other: 坐标系
        :return: 变换后坐标
        """
        vt = np.append(np.array(vt[:3]), 0)
        vt = vt @ self.ary4x4()
        if other is not None:
            vt = vt @ other.ary4x4inv()
        return vt[:3]

    def mcs(self, cs: vmi.CS4x4):
        """
        坐标系变换：坐标系cs由当前坐标系变换到世界坐标系，如果设置了other则变换到other坐标系
        坐标变换：世界坐标系中的局部坐标系cs经过当前变换得到新坐标系
        """
        cs = cs.ary4x4() @ self.ary4x4()
        return cs

    def translate(self, vt: np.ndarray) -> vmi.CS4x4:
        """
        串接平移变换
        :param vt: 3x1平移变换
        :return: 新坐标系
        """
        mat = np.array([[1, 0, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 1, 0],
                        [vt[0], vt[1], vt[2], 1]])
        self.ary4x4(self.ary4x4() @ mat)
        return self

    def rotate(self, angle: float, axis: np.ndarray, origin: np.ndarray = None) -> vmi.CS4x4:
        """
        串接旋转变换
        https://en.wikipedia.org/wiki/Rotation_matrix#In_three_dimensions

        :param angle: 旋转角度（deg）
        :param axis: 3x1旋转轴向量
        :param origin: 3x1旋转轴经过的一点
        :return: 新坐标系
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

    def reflect(self, normal: np.ndarray, origin: Optional[np.ndarray] = None) -> vmi.CS4x4:
        """
        串接反射变换
        https://en.wikipedia.org/wiki/Reflection_(mathematics)#Reflection_through_a_hyperplane_in_n_dimensions

        :param normal: 反射面法向量
        :param origin: 反射面经过的一点
        :return: 新坐标系
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

    def scale(self, factor: float, origin: Optional[np.ndarray] = None) -> vmi.CS4x4:
        """
        串接缩放变换

        :param factor: 缩放比例
        :param origin: 缩放投影中心
        :return: 新坐标系
        """
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


def CS4x4_InterLandmarks(pts0: List[np.ndarray], pts1: List[np.ndarray]) -> vmi.CS4x4:
    """
    对应点列变换，计算点列pts0到点列pts1的最小二乘变换

    :param pts0: 点列
    :param pts1: 点列
    :return: 坐标系
    """
    if len(pts0) > 2 and len(pts1) > 2:
        pts = [vtk.vtkPoints(), vtk.vtkPoints()]
        for pt in pts0:
            pts[0].InsertNextPoint([pt[0], pt[1], pt[2]])
        for pt in pts1:
            pts[1].InsertNextPoint([pt[0], pt[1], pt[2]])

        lt = vtk.vtkLandmarkTransform()
        lt.SetSourceLandmarks(pts[0])
        lt.SetTargetLandmarks(pts[1])
        lt.SetModeToRigidBody()
        lt.Update()

        mat = vtk.vtkMatrix4x4()
        lt.GetMatrix(mat)

        cs = CS4x4()
        cs.vtkmat4x4(mat)
        return cs


def ptOnPlane(pt: np.ndarray, origin: np.ndarray, normal: np.ndarray) -> np.ndarray:
    """
    计算点到平面投影

    :param pt: 初始点
    :param origin: 相关平面经过一点
    :param normal: 相关平面法向量
    :return: 投影后的点
    """
    pt, origin, normal = np.array(pt), np.array(origin), np.array(normal)
    return pt - normal * np.dot(pt - origin, normal)


def vtOnPlane(vt: np.ndarray, normal: np.ndarray) -> np.ndarray:
    """
    计算向量到平面投影

    :param vt: 初始向量
    :param normal: 相关平面法向量
    :return: 投影后的向量
    """
    vt, normal = np.array(vt), np.array(normal)
    n2 = np.dot(normal, normal)
    n2 = n2 if n2 != 0 else 1
    t = np.dot(vt, normal)
    return vt - t * normal / n2


def vtOnVector(vt: np.ndarray, vector: np.ndarray) -> np.ndarray:
    """
    计算向量到向量投影
    :param vt: 初始向量
    :param vector: 相关向量
    :return: 投影后的向量
    """
    dot = np.dot(vector, vector)
    if dot == 0:
        return np.zeros(3)
    return np.dot(vt, vector) / dot * vector
