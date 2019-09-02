import vmi
import numpy as np


def reslice_blend():
    left_top = view[1].pickFPlane([0, 0])  # 拾取视图左上角的焦平面点
    right_top = view[1].pickFPlane([view[1].width(), 0])  # 拾取视图右上角的焦平面点
    left_bottom = view[1].pickFPlane([0, view[1].height()])  # 拾取视图左下角的焦平面点

    cs = view[1].cameraCS()  # 获得视角坐标系

    xl = np.linalg.norm(left_top - right_top)  # 视图左右方向的真实尺度
    yl = np.linalg.norm(left_top - left_bottom)  # 视图上下方向的真实尺度
    zl = vmi.imSize_Vt(image, cs.axis(2))  # 图像沿视图入射方向的最大包围盒尺寸

    pt = vmi.imCenter(image) - 0.5 * zl * cs.axis(2)  # 计算图像包围盒中心到近平面投影点
    cs.origin(vmi.ptOnPlane(cs.origin(), pt, cs.axis(2)))  # 将坐标系原点投影到近平面

    # 重采样，图像范围外的体素值默认为-1024背景值
    image_reslice = vmi.imReslice(image, cs, [xl, yl, zl], -1024)

    # 将vtkImageData转换为numpy数组，沿z方向混叠，注意在numpy数组中，第1轴axis=0代表k轴
    image_blend = vmi.imArray_VTK(image_reslice)
    image_blend = image_blend.mean(axis=0)

    # 设置混叠图像的数据坐标范围，二维图像为[imin, imax, jmin, jmax, 0, 0]
    ext = vmi.imExtent(image_reslice)
    ext[4] = ext[5] = 0

    # 将numpy数组转换为vtkImageData
    image_blend = vmi.imVTK_Array(image_blend,
                                  vmi.imOrigin(image_reslice),
                                  vmi.imSpacing(image_reslice),
                                  ext)

    # 更新视图
    blend_prop.clone(image_blend)
    blend_prop.windowAuto()
    view[0].cameraFit()


if __name__ == '__main__':
    from PySide2.QtWidgets import QWidget, QHBoxLayout
    from vmi.example.read_dicom_slice_view import read_dicom

    image = read_dicom()  # 读取DICOM路径
    if image is None:
        vmi.appexit()

    iso_value = vmi.askInt(-1000, 200, 3000, None, 'HU')  # 用户输入-1000HU至3000HU范围内的一个CT值
    if iso_value is None:
        vmi.appexit()

    view = [vmi.View(), vmi.View()]
    blend_prop = vmi.ImageSlice(view[0])

    menu = vmi.Menu()
    view[1].mouse['RightButton']['PressRelease'] = menu.menuexec

    menu.menu.addAction('重采样混叠').triggered.connect(reslice_blend)
    menu.menu.addSeparator()
    menu.menu.addMenu(view[1].menu)

    mesh_prop = vmi.PolyActor(view[1], rgb=[1, 1, 0.6])  # 面绘制显示
    mesh_prop.clone(vmi.imIsosurface(image, iso_value))
    view[1].cameraFit()

    # 创建窗口包含两个视图
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.addWidget(view[0])
    layout.addWidget(view[1])

    vmi.appexec(widget)  # 执行主窗口程序
    vmi.appexit()  # 清理并退出程序
