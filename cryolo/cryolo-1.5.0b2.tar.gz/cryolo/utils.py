#
# COPYRIGHT
#
# All contributions by Ngoc Anh Huyn:
# Copyright (c) 2017, Ngoc Anh Huyn.
# All rights reserved.
#
# All contributions by Thorsten Wagner:
# Copyright (c) 2017 - 2019, Thorsten Wagner.
# All rights reserved.
#
# ---------------------------------------------------------------------------
#         Do not reproduce or redistribute, in whole or in part.
#      Use of this code is permitted only under licence from Max Planck Society.
#            Contact us at thorsten.wagner@mpi-dortmund.mpg.de
# ---------------------------------------------------------------------------
#
import numpy as np
import sys

from . import imagereader

class Filament:
    def __init__(self, boxes=None):

        if boxes is None:
            self.boxes = []
        else:
            self.boxes = boxes

    def add_box(self, box):
        self.boxes.append(box)
        return self

    def get_num_boxes(self):
        return len(self.boxes)

    def does_overlap(self, box, treshold):

        for filbox in self.boxes:
            if bbox_iou(filbox, box) >= treshold:
                return True
        return False


class BoundBox:
    def __init__(self, x, y, w, h, c=None, classes=None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.c = c
        self.classes = classes

        self.label = -1
        self.score = -1
        self.info = None  # helping data during processing

    def get_label(self):
        if self.label == -1:
            self.label = np.argmax(self.classes)

        return self.label

    def get_score(self):
        # if self.score == -1:
        self.score = self.classes[self.get_label()]

        return self.score


class WeightReader:
    def __init__(self, weight_file):
        self.offset = 4
        self.all_weights = np.fromfile(weight_file, dtype="float32")

    def read_bytes(self, size):
        self.offset = self.offset + size
        return self.all_weights[self.offset - size : self.offset]

    def reset(self):
        self.offset = 4


def getEquidistantBoxes(box1, box2, parts):
    points = zip(
        np.linspace(box1.x, box2.x, parts + 1, endpoint=True),
        np.linspace(box1.y, box2.y, parts + 1, endpoint=True),
    )
    new_boxes = []
    if box1.c is None or box2.c is None:
        c = 1
    else:
        c = (box1.c + box2.c) / 2
    classes = ""
    if box1.classes:
        classes = box1.classes
    w = box1.w
    h = box2.w
    for point in points:
        b = BoundBox(x=point[0], y=point[1], w=w, h=h, c=c, classes=classes)
        new_boxes.append(b)
    return new_boxes

def resample_filaments(new_filaments, box_distance):
    resamples_filaments = []
    for fil in new_filaments:
        res_fil = resample_filament(fil, box_distance)
        if not res_fil.boxes:
            prevbox = None
            for box in fil.boxes:
                if prevbox is None:
                    print(box.x, box.y)
                else:
                    print(
                        box.x,
                        box.y,
                        np.sqrt(box_squared_distance(prevbox, box)),
                    )
                prevbox = box
        else:
            resamples_filaments.append(res_fil)
    return resamples_filaments

def resample_filament(filament, distance):

    # Find two boxes with maximum distance
    boxes = filament.boxes
    max_distance = 0
    max_boxa = None
    max_boxb = None

    for i in range(len(boxes)):
        for j in range(len(boxes)):
            if i == j:
                continue
            dist = box_squared_distance(boxes[i], boxes[j])
            if dist > max_distance:
                max_boxa = i
                max_boxb = j
    if max_boxa is not None:
        # Construct a polyline, start from max_boxa
        polyline = []
        polyline.append(boxes[max_boxa])
        assigned_boxes = []
        assigned_boxes.append(max_boxa)
        last_appended_box = boxes[max_boxa]
        last_appended_index = max_boxa
        added_new = True

        while added_new:
            min_distance = 99999999
            nearest_box_index = None
            added_new = False
            for i in range(len(boxes)):
                if i == last_appended_index:
                    continue
                if i in assigned_boxes:
                    continue

                measured_distance = box_squared_distance(last_appended_box, boxes[i])

                if measured_distance < min_distance:
                    nearest_box_index = i
                    min_distance = measured_distance

            if nearest_box_index is not None:
                polyline.append(boxes[nearest_box_index])
                assigned_boxes.append(nearest_box_index)
                last_appended_box = boxes[nearest_box_index]
                last_appended_index = nearest_box_index
                added_new = True

        # Create new boxes based on the polyline
        new_boxes_candidates = []
        sqdistance = distance * distance

        for i in range(len(polyline) - 1):
            eq_boxes = getEquidistantBoxes(polyline[i], polyline[i + 1], parts=100)
            new_boxes_candidates.extend(eq_boxes)
        new_boxes = []
        dist = -1
        for box in new_boxes_candidates:
            if dist == -1:
                new_boxes.append(box)
                dist = 0
            else:
                dist = box_squared_distance(new_boxes[len(new_boxes) - 1], box)
                if dist > sqdistance:
                    new_boxes.append(box)

        new_filament = Filament()
        for box in new_boxes:
            new_filament.add_box(box)

        return new_filament
    return None


def box_squared_distance(boxa, boxb):
    return np.square(boxa.x - boxb.x) + np.square(boxa.y - boxb.y)


def box_to_N_x_M_array(boxes):
    data = np.empty(shape=(len(boxes), 2))

    for i in range(len(boxes)):
        data[i][0] = boxes[i].x
        data[i][1] = boxes[i].y
    return data


def normalize(image, margin_size=0):
    if not np.issubdtype(image.dtype, np.float32):
        image = image.astype(np.float32)
    mask = np.s_[ int(image.shape[0]*(margin_size)):int(image.shape[0]*(1-margin_size)), int(image.shape[1]*margin_size):int(image.shape[1]*(1-margin_size))]
    img_mean = np.mean(image[mask])
    img_std = np.std(image[mask])

    image = (image - img_mean) / (3 * 2 * img_std)


    return image


def bbox_iou(box1, box2):

    x1_min = box1.x - box1.w / 2
    x1_max = box1.x + box1.w / 2
    y1_min = box1.y - box1.h / 2
    y1_max = box1.y + box1.h / 2

    x2_min = box2.x - box2.w / 2
    x2_max = box2.x + box2.w / 2
    y2_min = box2.y - box2.h / 2
    y2_max = box2.y + box2.h / 2

    intersect_w = interval_overlap([x1_min, x1_max], [x2_min, x2_max])
    intersect_h = interval_overlap([y1_min, y1_max], [y2_min, y2_max])

    intersect = intersect_w * intersect_h

    union = box1.w * box1.h + box2.w * box2.h - intersect

    return float(intersect) / union


def interval_overlap(interval_a, interval_b):
    x1, x2 = interval_a
    x3, x4 = interval_b

    if x3 < x1:
        if x4 < x1:
            return 0
        else:
            return min(x2, x4) - x1
    else:
        if x2 < x3:
            return 0
        else:
            return min(x2, x4) - x3


def decode_netout(netout, obj_threshold, nms_threshold, anchors, nb_class):
    grid_h, grid_w, nb_box = netout.shape[:3]

    boxes = []

    # decode the output by the network
    netout[..., 4] = sigmoid(netout[..., 4])
    netout[..., 5:] = netout[..., 4][..., np.newaxis] * softmax(netout[..., 5:])
    netout[..., 5:] *= netout[..., 5:] > obj_threshold

    for row in range(grid_h):
        for col in range(grid_w):
            for b in range(nb_box):
                # from 4th element onwards are confidence and class classes
                classes = netout[row, col, b, 5:]

                if np.sum(classes) > 0:
                    # first 4 elements are x, y, w, and h
                    x, y, w, h = netout[row, col, b, :4]

                    x = (
                        col + sigmoid(x)
                    ) / grid_w  # center position, unit: image width
                    y = (
                        row + sigmoid(y)
                    ) / grid_h  # center position, unit: image height
                    w = anchors[2 * b + 0] * np.exp(w) / grid_w  # unit: image width
                    h = anchors[2 * b + 1] * np.exp(h) / grid_h  # unit: image height
                    confidence = netout[row, col, b, 4]

                    box = BoundBox(x, y, w, h, confidence, classes)

                    boxes.append(box)

    # suppress non-maximal boxes
    for c in range(nb_class):
        sorted_indices = list(reversed(np.argsort([box.classes[c] for box in boxes])))

        for i in range(len(sorted_indices)):
            index_i = sorted_indices[i]

            if boxes[index_i].classes[c] == 0:
                continue
            else:
                for j in range(i + 1, len(sorted_indices)):
                    index_j = sorted_indices[j]

                    if bbox_iou(boxes[index_i], boxes[index_j]) >= nms_threshold:
                        boxes[index_j].classes[c] = 0

    # remove the boxes which are less likely than a obj_threshold
    boxes = [box for box in boxes if box.get_score() > obj_threshold]

    return boxes


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def softmax(x, axis=-1, t=-100.0):
    x = x - np.max(x)

    if np.min(x) < t:
        x = x / np.min(x) * t

    e_x = np.exp(x)

    return e_x / e_x.sum(axis, keepdims=True)


def filter_images_nn_img(img_path, model_path, padding=15, batch_size=4):
    import h5py
    from janni import predict as janni_predict
    from janni import models as janni_models
    with h5py.File(model_path, mode="r") as f:
        try:
            import numpy as np
            model = str(np.array((f["model_name"])))
            patch_size = tuple(f["patch_size"])
        except KeyError:
            print("Not supported filtering model. Stop.")
            sys.exit(0)

    if model == "unet":
        model = janni_models.get_model_unet(input_size=patch_size)
        model.load_weights(model_path)
    else:
        print("Not supported model", model, "Stop")
        sys.exit(0)

    image = imagereader.image_read(img_path)
    fitlered_img = janni_predict.predict_np(model,
                                              image,
                                              patch_size=(1024, 1024),
                                              padding=padding,
                                              batch_size=batch_size)

    return fitlered_img

def filter_images_nn_dir(img_paths, output_dir_filtered_imgs, model_path, padding=15, batch_size=4):
    import h5py
    from janni import predict as janni_predict
    from janni import models as janni_models
    with h5py.File(model_path, mode="r") as f:
        try:
            import numpy as np
            model = str(np.array((f["model_name"])))
            patch_size = tuple(f["patch_size"])
        except KeyError:
            print("Not supported filtering model. Stop.")
            sys.exit(0)

    if model == "unet":
        model = janni_models.get_model_unet(input_size=patch_size)
        model.load_weights(model_path)
    else:
        print("Not supported model", model, "Stop")
        sys.exit(0)


    filtered_paths = janni_predict.predict_list(
        image_paths = img_paths,
        output_path = output_dir_filtered_imgs,
        model=model,
        patch_size=patch_size,
        padding=padding,
        batch_size=batch_size)

    return filtered_paths