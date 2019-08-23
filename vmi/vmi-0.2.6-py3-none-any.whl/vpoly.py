import vtk
import vmi
import numpy as np


def pdExtract_Largest(pd: vtk.vtkPolyData):
    connectivity = vtk.vtkPolyDataConnectivityFilter()
    connectivity.SetInputData(pd)
    connectivity.SetExtractionModeToLargestRegion()
    connectivity.Update()
    return connectivity.GetOutput()


def pdExtract_Closest(pd: vtk.vtkPolyData, closest_point):
    connectivity = vtk.vtkPolyDataConnectivityFilter()
    connectivity.SetInputData(pd)
    connectivity.SetExtractionModeToClosestPointRegion()
    connectivity.SetClosestPoint([closest_point[i] for i in range(3)])
    connectivity.Update()
    return connectivity.GetOutput()


def pdSmoothWindowedSinc(pd: vtk.vtkPolyData, iter_num=20):
    smooth = vtk.vtkWindowedSincPolyDataFilter()
    smooth.SetInputData(pd)
    smooth.SetNumberOfIterations(iter_num)
    smooth.SetPassBand(0.1)
    smooth.SetNonManifoldSmoothing(1)
    smooth.SetNormalizeCoordinates(1)
    smooth.SetFeatureAngle(60)
    smooth.SetBoundarySmoothing(0)
    smooth.SetFeatureEdgeSmoothing(0)
    smooth.Update()
    return smooth.GetOutput()


def pdSmoothLaplacian(pd: vtk.vtkPolyData, iter_num=20):
    smooth = vtk.vtkSmoothPolyDataFilter()
    smooth.SetInputData(pd)
    smooth.SetNumberOfIterations(iter_num)
    smooth.SetConvergence(0)
    smooth.SetRelaxationFactor(0.33)
    smooth.SetFeatureAngle(60)
    smooth.SetBoundarySmoothing(0)
    smooth.SetFeatureEdgeSmoothing(0)
    smooth.Update()
    return smooth.GetOutput()


def pdNormals(pd: vtk.vtkPolyData):
    if pd.GetPointData().GetNormals() is None or pd.GetCellData().GetNormals() is None:
        normals = vtk.vtkPolyDataNormals()
        normals.SetInputData(pd)
        normals.SetComputePointNormals(1)
        normals.SetComputeCellNormals(1)
        normals.Update()
        return normals.GetOutput()
    return pd


def pdTriangle(pd: vtk.vtkPolyData, pass_verts=1, pass_lines=1):
    triangle = vtk.vtkTriangleFilter()
    triangle.SetPassVerts(pass_verts)
    triangle.SetPassLines(pass_lines)
    triangle.SetInputData(pd)
    triangle.Update()
    return triangle.GetOutput()


def pdClip_Implicit(pd: vtk.vtkPolyData, clip_function: vtk.vtkImplicitFunction):
    clip = vtk.vtkClipPolyData()
    clip.SetClipFunction(clip_function)
    clip.SetInputData(pdNormals(pd))
    clip.Update()
    return [clip.GetOutput(), clip.GetClippedOutput()]


def pdClip_Pd(pd: vtk.vtkPolyData, clip_pd: vtk.vtkPolyData):
    clip_function = vtk.vtkImplicitPolyDataDistance()
    clip_function.SetInput(pdNormals(clip_pd))
    return pdClip_Implicit(pd, clip_function)


def pdAppend(pds):
    append = vtk.vtkAppendPolyData()
    for pd in pds:
        append.AddInputData(pd)
    append.Update()
    return append.GetOutput()


def pdClean(pd: vtk.vtkPolyData, point_merging=1):
    clean = vtk.vtkCleanPolyData()
    clean.SetInputData(pd)
    clean.SetPointMerging(point_merging)
    clean.Update()
    return clean.GetOutput()


def pdBoolean_Union(pd0: vtk.vtkPolyData, pd1: vtk.vtkPolyData):
    boolean = vtk.vtkLoopBooleanPolyDataFilter()
    boolean.SetOperationToUnion()
    boolean.SetInputData(0, pdNormals(pd0))
    boolean.SetInputData(1, pdNormals(pd1))
    boolean.Update()
    return boolean.GetOutput()


def pdBoolean_Intersection(pd0: vtk.vtkPolyData, pd1: vtk.vtkPolyData):
    boolean = vtk.vtkLoopBooleanPolyDataFilter()
    boolean.SetOperationToIntersection()
    boolean.SetInputData(0, pdNormals(pd0))
    boolean.SetInputData(1, pdNormals(pd1))
    boolean.Update()
    return boolean.GetOutput()


def pdBoolean_Difference(pd0: vtk.vtkPolyData, pd1: vtk.vtkPolyData):
    boolean = vtk.vtkLoopBooleanPolyDataFilter()
    boolean.SetOperationToDifference()
    boolean.SetInputData(0, pdNormals(pd0))
    boolean.SetInputData(1, pdNormals(pd1))
    boolean.Update()
    return boolean.GetOutput()


def pdRayCast_Pt(pt, vt, base: vtk.vtkPolyData, base_kd=None, base_obb=None):
    pt = np.array([pt[i] for i in range(3)])
    vt = np.array([vt[i] for i in range(3)])
    vt /= np.linalg.norm(vt)

    bnd = base.GetBounds()
    d1 = np.array([bnd[1] - bnd[0], bnd[3] - bnd[2], bnd[5] - bnd[4]])
    d1 = np.linalg.norm(d1)

    if base_kd is None:
        base_kd = vtk.vtkKdTreePointLocator()
        base_kd.SetDataSet(base)
        base_kd.BuildLocator()

    cid = base_kd.FindClosestPoint(pt)

    cpt = np.array(base.GetPoint(cid))
    d2 = np.linalg.norm(pt - cpt)

    pt_proj = pt + (d1 + d2) * vt

    if base_obb is None:
        base_obb = vtk.vtkOBBTree()
        base_obb.SetDataSet(base)
        base_obb.BuildLocator()

    pts = vtk.vtkPoints()
    base_obb.IntersectWithLine(pt, pt_proj, pts, None)

    if pts.GetNumberOfPoints() > 0:
        return np.linalg.norm(pt - np.array(pts.GetPoint(0)))
    else:
        return None


def pdRayCast_Pd(pd: vtk.vtkPolyData, vt, base: vtk.vtkPolyData, default_distance=None):
    vt = np.array([vt[i] for i in range(3)])
    vt /= np.linalg.norm(vt)

    base_kd = vtk.vtkKdTreePointLocator()
    base_kd.SetDataSet(base)
    base_kd.BuildLocator()

    base_obb = vtk.vtkOBBTree()
    base_obb.SetDataSet(base)
    base_obb.BuildLocator()

    out = vtk.vtkPolyData()
    out.DeepCopy(pd)

    for i in range(pd.GetNumberOfPoints()):
        pt = pd.GetPoint(i)
        d = pdRayCast_Pt(pt, vt, base, base_kd, base_obb)

        if default_distance is not None:
            if d is None or d > default_distance:
                d = default_distance

        if d is not None:
            pt = pt + d * vt
            out.GetPoints().SetPoint(i, pt)

    return out
