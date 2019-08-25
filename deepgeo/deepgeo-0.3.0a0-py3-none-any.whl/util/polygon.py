import numpy as np
from skimage.measure import find_contours
from matplotlib.patches import Polygon

import math as Math

def simplify(polygons):
    simply = []
    for polygon in polygons:
        tpoint = None
        points = []
        for point in polygon:
            if tpoint is None:
                tpoint = point
                points.append(tpoint.tolist())
            else:
                if tpoint[0] != point[0] and tpoint[1] != point[1]:
                    points.append(tpoint.tolist())
                tpoint = point
        if points[0][0] != points[-1][0] and points[0][1] != points[-1][1]:
            points.append(points[0])
        simply.append(points)
    return simply

def get_info(polygons):
    x_list = []
    y_list = []
    for p in polygons:
        x_list.append(p[0])
        y_list.append(p[1])
    x_max = max(x_list)
    y_max = max(y_list)
    x_min = min(x_list)
    y_min = min(y_list)
    avgX = (x_max + x_min) / 2
    avgY = (y_max + y_min) / 2
    distance = (x_max-x_min,y_max-y_min)
    center_point = (avgX,avgY)
    info_dic = {'distance': distance,'center_point':center_point, 'diagonal':[x_max,y_max,x_min,y_min]}
    return info_dic

def to_box(polygons):
    info = get_info(polygons)
    return info['diagonal']

def to_center_point(polygons):
    info = get_info(polygons)
    return info['center_point']

def to_distance(polygons):
    info = get_info(polygons)
    return info['distance']

def to_fov(x, y, direction, distance, view_angle):
    times = 1
    x4 = x
    y4 = y

    x2 = x + distance * 2 / Math.sqrt(3) * Math.sin(Math.radians(direction + view_angle / 2)) * times
    y2 = y + distance * 2 / Math.sqrt(3) * Math.cos(Math.radians(direction + view_angle / 2)) * times

    x3 = x + distance * 2 / Math.sqrt(3) * Math.sin(Math.radians(direction - view_angle / 2)) * times
    y3 = y + distance * 2 / Math.sqrt(3) * Math.cos(Math.radians(direction - view_angle / 2)) * times

    return "POLYGON((" + str(x4) + " " + str(y4) + ", " + str(x2) + " " + str(y2) + ", " + str(x3) + " " + str(
        y3) + ", " + str(x4) + " " + str(y4) + "))"

def from_numpy(masks, is_simplify=True):
    # Number of instances
    data = []
    num = masks.shape[-1]
    for i in range(num):
        # Mask
        mask = masks[:, :, i]
        padded_mask = np.zeros(
            (mask.shape[0] + 2, mask.shape[1] + 2), dtype=np.uint8)
        padded_mask[1:-1, 1:-1] = mask
        contours = find_contours(padded_mask, 0.5)
        for verts in contours:
            # Subtract the padding and flip (y, x) to (x, y)
            verts = np.fliplr(verts) - 1
            data.append(Polygon(verts).get_path().vertices)
    if is_simplify:
        return simplify(data)
    else:
        return data