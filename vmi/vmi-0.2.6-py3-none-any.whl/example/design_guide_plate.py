import vmi
import numpy as np


def read_stl():
    file_name = vmi.askOpenFile('*.stl')
    if file_name is not None:
        pd = vmi.vtkread_STL(file_name)
        if pd.GetNumberOfCells() > 0:
            return pd


def LeftButtonPress(**kwargs):
    """响应左键按下"""
    if kwargs['picked'] is mesh_prop:
        pt = view.mouseOnPropCell()
        path_pts.clear()
        path_pts.append(pt)
        rebuild_path(path_pts)


def LeftButtonPressMove(**kwargs):
    """响应左键按下之后移动"""
    if kwargs['picked'] is mesh_prop:
        pt = view.mouseOnPropCell()
        rebuild_path([*path_pts, pt])
        if view.mouseOnProp() is mesh_prop:
            path_pts.append(pt)


def LeftButtonPressMoveRelease(**kwargs):
    """响应左键按下移动之后释放"""
    if kwargs['picked'] is mesh_prop:
        rebuild_plate()


def rebuild_path(pts):
    if len(pts) > 1:
        path_shape_data.clone(vmi.ccWire(vmi.ccSegments(pts)))
    else:
        path_shape_data.clone()
    view.updateInTime()


def rebuild_plate():
    if len(path_pts) > 1:
        cs = view.cameraCS()
        solids = []
        for center in [path_pts[0], path_pts[-1]]:
            h = plate_outer_radius  # 圆柱半高等于外半径
            end_center = [cs.mpt([0, 0, -h], origin=center),
                          cs.mpt([0, 0, h], origin=center)]
            end_wire = [vmi.ccWire(vmi.ccCircle_CS(end_center[0], plate_outer_radius + 1, cs)),
                        vmi.ccWire(vmi.ccCircle_CS(end_center[1], plate_outer_radius, cs))]
            end_face = [vmi.ccFace(end_wire[0]),
                        vmi.ccFace(end_wire[1])]
            profile = vmi.ccLoft([end_wire[0], end_wire[1]], True)
            shell = vmi.ccSew([end_face[0], end_face[1], profile])
            solid = vmi.ccSolid(shell)

            plate_pd = vmi.ccPd_Sh(end_face[1])
            plate_pd = vmi.pdTriangle(plate_pd, 0, 0)
            plate_pd = vmi.pdRayCast_Pd(plate_pd, -cs.axis(2), mesh_pd, 2 * h)

            # plate_pd = vmi.poBoolean_Difference(plate_pd, mesh_pd)
            # plate_pd = vmi.poExtract_Largest(plate_pd)
            solids.append(plate_pd)

        plate_prop.clone(vmi.pdAppend(solids))
        plate_prop.rep('wireframe')
        # mesh_prop.visible(False)
    else:
        plate_prop.clone()
    view.updateInTime()


if __name__ == '__main__':
    from PySide2.QtWidgets import QAction

    mesh_pd = read_stl()  # 读取STL文件到单元数据
    if mesh_pd is None:
        vmi.appexit()

    mesh_pd = vmi.cgPd_Ph(vmi.cgPh_Pd(mesh_pd))

    view = vmi.View()  # 视图

    # 面网格模型
    mesh_prop = vmi.PolyActor(view)
    mesh_prop.color([1, 1, 0.6])  # 颜色
    mesh_prop.pickable(True)  # 设置可拾取
    mesh_prop.mouse['LeftButton']['Press'] = LeftButtonPress
    mesh_prop.mouse['LeftButton']['PressMove'] = LeftButtonPressMove
    mesh_prop.mouse['LeftButton']['PressMoveRelease'] = LeftButtonPressMoveRelease
    mesh_prop.clone(mesh_pd)

    # 拾取路径
    path_pts = []
    path_shape_data = vmi.ShapeData()
    path_prop = vmi.PolyActor(view, shape_data=path_shape_data)
    path_prop.color([1, 0.4, 0.4])  # 颜色
    path_prop.size(line=3)

    # 导板
    plate_hole_axis = np.array([0, 0, 1])
    plate_outer_radius = 5
    plate_inner_radius = 1
    plate_prop = vmi.PolyActor(view)
    plate_prop.color([0.4, 0.6, 1])  # 颜色

    view.cameraFit()
    vmi.appexec(view)  # 执行主窗口程序
    vmi.appexit()  # 清理并退出程序
