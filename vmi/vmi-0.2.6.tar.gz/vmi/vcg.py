from CGAL.CGAL_AABB_tree import *
from CGAL.CGAL_Kernel import *
from CGAL.CGAL_Convex_hull_2 import *
from CGAL.CGAL_Mesh_3 import *
from CGAL.CGAL_Spatial_searching import *
from CGAL.CGAL_Triangulation_2 import *
from CGAL.CGAL_HalfedgeDS import *
from CGAL.CGAL_Triangulation_3 import *
from CGAL.CGAL_Alpha_shape_2 import *
from CGAL.CGAL_Polyhedron_3 import *
from CGAL.CGAL_Voronoi_diagram_2 import *
from CGAL.CGAL_Mesh_2 import *
from CGAL.CGAL_Interpolation import *
from CGAL.CGAL_Box_intersection_d import *
from CGAL.CGAL_Convex_hull_3 import *
from CGAL.CGAL_Point_set_processing_3 import *
from CGAL.CGAL_Polyline_simplification_2 import *
from CGAL.CGAL_Advancing_front_surface_reconstruction import *
from CGAL.CGAL_Polygon_mesh_processing import *
from CGAL import *

import vmi
import vtk


def cgPh_Pd(pd: vtk.vtkPolyData):
    num_vertex = pd.GetNumberOfPoints()
    num_facet = 0
    for i in range(pd.GetNumberOfCells()):
        cell: vtk.vtkCell = pd.GetCell(i)
        if cell.GetCellType() in [vtk.VTK_TRIANGLE, vtk.VTK_QUAD, vtk.VTK_POLYGON]:
            num_facet += 1

    m = Polyhedron_modifier()
    m.begin_surface(num_vertex, num_facet)

    for i in range(pd.GetNumberOfPoints()):
        pt = pd.GetPoint(i)
        m.add_vertex(Point_3(pt[0], pt[1], pt[2]))

    for cell_id in range(pd.GetNumberOfCells()):
        cell: vtk.vtkCell = pd.GetCell(cell_id)
        if cell.GetCellType() in [vtk.VTK_TRIANGLE, vtk.VTK_QUAD, vtk.VTK_POLYGON]:
            m.begin_facet()
            for ii in range(cell.GetPointIds().GetNumberOfIds()):
                pid = cell.GetPointId(ii)
                m.add_vertex_to_facet(pid)
            m.end_facet()

    m.end_surface()

    ph = Polyhedron_3()
    ph.delegate(m)
    return ph


def cgPd_Ph(ph: Polyhedron_3):
    pd = vtk.vtkPolyData()
    pd.SetPoints(vtk.vtkPoints())
    pd.SetPolys(vtk.vtkCellArray())

    points, i = {}, 0
    for vertex in ph.vertices():
        p = vertex.point()
        pd.GetPoints().InsertNextPoint([p.x(), p.y(), p.z()])
        points[str(p)] = i
        i += 1

    for facet in ph.facets():
        halfedge = facet.halfedge()
        cell_ids = []

        while len(cell_ids) == 0 or halfedge != facet.halfedge():
            cell_ids.append(points[str(halfedge.vertex().point())])
            halfedge = halfedge.next()

        n = len(cell_ids)

        if n == 3:
            cell = vtk.vtkTriangle()
            for i in range(n):
                cell.GetPointIds().SetId(i, cell_ids[i])
            pd.GetPolys().InsertNextCell(cell)
        elif n == 4:
            cell = vtk.vtkQuad()
            for i in range(n):
                cell.GetPointIds().SetId(i, cell_ids[i])
            pd.GetPolys().InsertNextCell(cell)
        elif n > 4:
            cell = vtk.vtkPolygon()
            cell.GetPointIds().SetNumberOfIds(n)
            for i in range(n):
                cell.GetPointIds().SetId(i, cell_ids[i])
            pd.GetPolys().InsertNextCell(cell)

    return pd


if __name__ == '__main__':
    view = vmi.View()  # 视图

    view.cameraFit()
    vmi.appexec(view)  # 执行主窗口程序
    vmi.appexit()  # 清理并退出程序
