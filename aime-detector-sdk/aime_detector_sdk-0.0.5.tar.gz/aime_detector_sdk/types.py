class DetectConfigs:
    def __init__(self, w, h, resize_out_ratio=4.0, threshold_distance=100.0, redzone_threshold_distance=100.0, max_fps=10,
                 delay_detected=0.5, max_miss=3.0):
        self.w = w  # Width of single video frame
        self.h = h  # Height of single video frame
        self.resize_out_ratio = resize_out_ratio
        self.threshold_distance = threshold_distance  # Farthest distance to keep in conversation
        self.redzone_threshold_distance = redzone_threshold_distance  # Farthest distance to start greeting
        self.max_fps = max_fps  # Maximum frame per second to process
        self.max_miss = max_miss  # Maximum time to be wait before terminate the conversation
        self.delay_detected = delay_detected  # Maximum time to be wait before start the conversation


class VisionDetectorHuman:
    class FaceBox:
        def __init__(self, left, top, right, bottom):
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom

    def __init__(self, id, name, distance, face_box: FaceBox, portrait=None):
        """
        :type id: ID of detected human
        :type name: Name of detected human. Used in greeting message
        :type distance: Estimated distance from camera to human
        :type face_box: Rectangle coordinate of face in image frame
        :type portrait: Sliced image for human face
        """
        self.id = id
        self.name = name
        self.distance = distance
        self.face_box = face_box
        self.portrait = portrait
        self.fresh = True  # Is this human found in detected frame
        self.timestamp_in_range = None  # First detected timestamp

    def get(self, key, default=None):
        return getattr(self, key, default=default)

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        setattr(self, key, value)
