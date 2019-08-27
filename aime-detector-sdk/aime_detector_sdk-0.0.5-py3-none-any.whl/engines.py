import time
from typing import Any, Generator, List, Tuple

import cv2

from . import utilities
from .types import VisionDetectorHuman, DetectConfigs


class BaseDetector:
    def __init__(self, configs: DetectConfigs, **kwargs):
        self.configs = configs
        self.register_hook = None
        if 'register_hook' in kwargs:
            self.register_hook = kwargs['register_hook']

    def init(self):
        pass

    def run_detection(self, image_frames) -> Generator[Tuple[bool, bool, List, Any], None, None]:
        raise NotImplementedError()

    def start_register(self, name):
        pass

    def register_started(self):
        hook = self.register_hook
        if hook is not None:
            hook.on_started()

    def register_finished(self, error):
        hook = self.register_hook
        if hook is not None:
            hook.on_done(error)


class BaseVisionDetector(BaseDetector):

    def setup(self):
        pass

    def teardown(self):
        pass

    def check_motion_region(self, image):
        """
        Check for motion region. Detect if have motion in video or still image only
        :param image: cv2 image
        :return: has motion region
        """
        return True

    def detect_faces(self, image) -> List[VisionDetectorHuman]:
        """
        Get all faces detected.
        :param image: current cv2 video frame
        """
        raise NotImplementedError()

    def run_detection(self, image_frames):
        self.setup()
        w = self.configs.w
        h = self.configs.h
        threshold_distance = max(self.configs.threshold_distance, self.configs.redzone_threshold_distance)
        redzone_threshold_distance = min(self.configs.redzone_threshold_distance, self.configs.threshold_distance)

        distance_keep_conversation = threshold_distance
        distance_greeting = redzone_threshold_distance

        time_before_greeting = self.configs.delay_detected
        max_miss_second = self.configs.max_miss

        max_fps = float(self.configs.max_fps)
        max_frame_time = 1.0 / max_fps
        state = 'IDLE'  # IDLE mean no conversation
        person_miss_timestamp = None

        try:
            while True:
                tpf_start = time.time()
                try:
                    image = next(image_frames)
                    image = cv2.resize(image, (w, h))
                except StopIteration:
                    break
                if not self.check_motion_region(image):
                    yield False, False, None, image
                    continue

                detected_faces = self.detect_faces(image)
                if detected_faces is None or len(detected_faces) == 0:
                    if person_miss_timestamp is None:
                        person_miss_timestamp = time.time()
                else:
                    person_miss_timestamp = None

                drawn_result = utilities.draw_results(image, detected_faces)
                # yield the result
                person_found_changed, person_found = False, False
                detected_data = None
                if person_miss_timestamp is not None:
                    if state == 'ACTIVE' and time.time() - person_miss_timestamp > max_miss_second:
                        state = 'IDLE'
                        person_found_changed = True
                        person_miss_timestamp = None
                else:
                    in_range = False
                    first_time_in_range = float('inf')
                    detected_data = []
                    for item in detected_faces:
                        if item.fresh is True:
                            detected_data.append({'id': item.id, 'name': item.name, 'distance': item.distance, 'portrait': item.portrait})
                            if item.distance < distance_greeting:
                                in_range = True
                                first_time_in_range = min(first_time_in_range, item.timestamp_in_range)
                    if len(detected_data) > 0:
                        detected_data = sorted(detected_data, key=lambda d: d['distance'])
                    if in_range is True and time.time() - first_time_in_range > time_before_greeting and state == 'IDLE':
                        state = 'ACTIVE'
                        person_found_changed, person_found = True, True
                    else:
                        person_found = True

                yield person_found_changed, person_found, detected_data if person_found_changed and person_found else None, drawn_result
                tpf = time.time() - tpf_start
                if max_frame_time > tpf:
                    time.sleep(max_frame_time - tpf)
        finally:
            self.teardown()
