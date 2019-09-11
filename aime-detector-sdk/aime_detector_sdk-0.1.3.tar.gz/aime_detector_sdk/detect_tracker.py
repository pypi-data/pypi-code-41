import time
from typing import List

from .types import VisionDetectorHuman


class DetectTracker:
    def __init__(self, distance_keep, object_age=1.0):
        self.object_age = object_age
        self.distance_keep = distance_keep
        self.tracked_human_arr = []
        self.tracked_human = {}

    def update(self, new_humans: List[VisionDetectorHuman]):
        distance_keep = self.distance_keep
        tracked_human_arr = self.tracked_human_arr
        tracked_human = self.tracked_human
        dead_object_time = time.time() - self.object_age
        now_time = time.time()
        new_object = {}

        for human in new_humans:
            if human.distance > distance_keep:
                continue
            new_object[human.id] = True
            old_human = tracked_human.get(human.id)
            if old_human is None:
                human.timestamp_in_range = now_time
                tracked_human_arr.append(human)
                tracked_human[human.id] = human
                old_human = human
            else:
                old_human.distance = human.distance
                old_human.face_box = human.face_box
                old_human.portrait = human.portrait
            old_human.fresh = True
            old_human.last_timestamp_in_range = now_time

        dead_object = {}
        for human in tracked_human_arr:
            if human.last_timestamp_in_range < dead_object_time:
                dead_object[human.id] = human
            elif human.id not in new_object:
                human.fresh = False

        for obj_id, obj in dead_object.items():
            tracked_human_arr.remove(obj)
            del tracked_human[obj_id]

    def get_alive(self):
        return self.tracked_human_arr[:]
