import time
from typing import Any, Generator, List, Tuple

import cv2

from . import utilities
from .detect_tracker import DetectTracker
from .types import VisionDetectorHuman, DetectConfigs, FaceRegisterError


class BaseDetector:
    def __init__(self, configs: DetectConfigs, **kwargs):
        self.configs = configs
        self.register_hook = None
        self._is_registering_ = False
        if 'register_hook' in kwargs:
            self.register_hook = kwargs['register_hook']

    def init(self):
        pass

    def run_detection(self, image_frames) -> Generator[Tuple[bool, bool, List, Any], None, None]:
        raise NotImplementedError()

    def start_register(self, name: str):
        pass

    def register_started(self):
        self._is_registering_ = True
        hook = self.register_hook
        if hook is not None:
            hook.on_started()

    def register_finished(self, error=None):
        self._is_registering_ = False
        hook = self.register_hook
        if hook is not None:
            hook.on_done(error)


class BaseVisionDetector(BaseDetector):
    def __init__(self, configs: DetectConfigs, **kwargs):
        super().__init__(configs, **kwargs)
        self._pending_register_name_ = None

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

    def prepare_register_face(self, name: str) -> bool:
        """
        Prepare to register face
        :param name: Person name to be registered
        :return: True if prepare to register face success. Other wise register face request will be canceled
        """
        return False

    def register_face(self, image, human_data: List[VisionDetectorHuman]) -> Tuple[bool, int]:
        """
        Do save face image from camera frame
        :param image: current cv2 video frame
        :param human_data: List of human found
        :return: completed, count
        Raise FaceRegisterError if face register need to force completed because of error 
        """
        raise FaceRegisterError('Does not support register face')

    def start_register(self, name: str):
        self._pending_register_name_ = name

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
        tracker = DetectTracker(distance_keep_conversation)

        try:
            tpf_start = None
            while True:
                if tpf_start:
                    tpf = time.time() - tpf_start
                    if max_frame_time > tpf:
                        time.sleep(max_frame_time - tpf)
                tpf_start = time.time()
                try:
                    image = next(image_frames)
                    image = cv2.resize(image, (w, h))
                except StopIteration:
                    break
                if not self.check_motion_region(image):
                    if person_miss_timestamp is None:
                        person_miss_timestamp = time.time()
                    if state == 'ACTIVE' and person_miss_timestamp is not None and time.time() - person_miss_timestamp > max_miss_second:
                        state = 'IDLE'
                        person_miss_timestamp = None
                        yield True, False, None, image
                    else:
                        yield False, False, None, image
                    continue

                detected_faces = self.detect_faces(image)
                if detected_faces is None or len(detected_faces) == 0:
                    if person_miss_timestamp is None:
                        person_miss_timestamp = time.time()
                else:
                    person_miss_timestamp = None
                    # register face hook
                    if not self._is_registering_ and self._pending_register_name_ is not None:
                        if self.prepare_register_face(self._pending_register_name_):
                            self.register_started()
                        self._pending_register_name_ = None
                    if self._is_registering_:
                        try:
                            regis_ret = self.register_face(image, detected_faces)
                            if regis_ret is not None:
                                completed, captured = regis_ret
                                if completed:
                                    self.register_finished()
                                    detected_faces = self.detect_faces(image)  # re evaluate to update trained result
                                else:
                                    image = utilities.collect_watermark(image, captured)

                        except FaceRegisterError as e:
                            self.register_finished(e.message if e.message else 'Error occured')

                drawn_result = utilities.draw_results(image, detected_faces)
                if self._is_registering_:  # register mode active. Don't perform human detect check
                    yield False, False, None, drawn_result
                    continue
                tracker.update(detected_faces)
                detected_faces = tracker.get_alive()
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
                            detected_data.append({'id': item.id, 'name': item.name, 'distance': item.distance,
                                                  'portrait': item.portrait})
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
                detected_data = detected_data if person_found_changed and person_found else None
                yield person_found_changed, person_found, detected_data, drawn_result
        finally:
            self.teardown()
            if self._is_registering_:
                self.register_finished()
