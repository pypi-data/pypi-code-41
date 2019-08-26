from north_c9.controller import C9Controller


class RobotError(Exception):
    pass


class Robot:
    def __init__(self, controller: C9Controller):
        self.controller = controller
