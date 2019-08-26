import threading

import cv2

from .engines import BaseDetector
from .types import DetectConfigs


class DemoApp:
    def __init__(self, camera, detector: BaseDetector, configs: DetectConfigs, mirror_camera=False):
        self.camera = camera
        self.detector = detector
        self.configs = configs
        self.mirror_camera = mirror_camera

    def run(self):
        cam = FastCameraReader(self.camera, mirror_camera=self.mirror_camera, prefered_width=self.configs.w, prefered_height=self.configs.h)
        cam.start()
        try:
            for person_found_changed, person_found, human_data, image_frame in self.detector.run_detection(cam):
                if person_found_changed:
                    print('person found changed: ', person_found)
                    if person_found:
                        print('human data', human_data)
                cv2.imshow('Video', image_frame)
                if cv2.waitKey(1) == 27:
                    break
                elif cv2.getWindowProperty('Video', cv2.WND_PROP_VISIBLE) < 1:
                    break
        finally:
            cam.stop()


class FastCameraReader(threading.Thread):

    def __init__(self, camera, mirror_camera=False, prefered_width=640, prefered_height=480):
        super().__init__()
        self.camera_id = camera
        self.mirror_camera = mirror_camera

        self._stopped = False
        self._camera_started = False
        self._graped = False
        self._image = None
        self.cam = cv2.VideoCapture(camera)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, prefered_width)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, prefered_height)

    @property
    def is_opened(self):
        return self.cam.isOpened()

    def stop(self):
        self._stopped = True
        self.cam.release()

    def run(self):
        cam = self.cam
        try:
            self._graped, self._image = cam.read()
            self._camera_started = True
            while not self._stopped:
                self._graped, self._image = cam.read()
        finally:
            cam.release()

    def __iter__(self):
        return self

    def __next__(self):
        while not self._camera_started:
            if self._stopped:
                raise StopIteration()
            continue
        if self._stopped:
            raise StopIteration()
        ret_val, image = self._graped, self._image
        if not ret_val:
            raise StopIteration()
        if self.mirror_camera:
            image = cv2.flip(image, 1)  # flip image for human eye friendly
        return image
