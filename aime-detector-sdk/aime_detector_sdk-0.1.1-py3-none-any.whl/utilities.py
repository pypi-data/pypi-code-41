from typing import List

import cv2

from .types import VisionDetectorHuman


def draw_results(image, faces: List[VisionDetectorHuman]):
    for face in faces:
        draw_result(image, face)
    return image


def draw_result(image, face: VisionDetectorHuman):
    box = face.face_box
    if box is None:
        return
    id = face.id
    if isinstance(box, VisionDetectorHuman.FaceBox):
        l, t, r, b = box.left, box.top, box.right, box.bottom
    else:
        l, t, r, b = box
    if id is None:
        color = (0, 0, 255)
    else:
        if not isinstance(id, str):
            id = str(id)
        color = (0, 255, 0)
    cv2.rectangle(image, (l, t), (r, b), color, 2)
    if id is not None:
        put_text_label(image, (l, t), id, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), color, thickness=2, bottom=True)


def put_text_label(img, orig, text, font_face, font_scale, text_color, bg_color, thickness=1, bottom=False):
    size = cv2.getTextSize(text, font_face, font_scale, thickness)
    x, y = orig
    if bottom:
        cv2.rectangle(img, (x, y - size[0][1] - 6), (x + size[0][0] + 6, y), bg_color, cv2.FILLED)
        cv2.putText(img, text, (x + 3, y - 3), font_face, font_scale, text_color, thickness)
    else:
        cv2.rectangle(img, (x, y), (x + size[0][0] + 6, y + size[0][1] + 6), bg_color, cv2.FILLED)
        cv2.putText(img, text, (x + 3, y + size[0][1] + 3), font_face, font_scale, text_color, thickness)
