from tayuya import constants


class TrackError(Exception):
    def __init__(self):
        self.msg = constants.TRACK_ERROR_MESSAGE

    def __str__(self):
        return repr(self.msg)

