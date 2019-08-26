from typing import Optional, Union, Tuple, List
from north_utils.location import Vector3
from north_c9.axis import RevoluteAxis, PrismaticAxis, OpenOutput
from north_c9.controller import C9Controller
from north_robots.robot import Robot
from north_robots.components import Component, Location

MovementOrderItem = Union[int, Tuple[int, int], Tuple[int, int, int]]
MovementOrder = List[MovementOrderItem]


class N9RobotError(Exception):
    pass


class N9RobotMovementError(N9RobotError):
    pass


class N9RobotMovementUnreachableLocation(N9RobotMovementError):
    pass


class N9RobotMovementInvalidMovementOrder(N9RobotMovementError):
    pass


class N9Robot(Robot):
    GRIPPER = 0
    ELBOW = 1
    SHOULDER = 2
    COLUMN = 3

    MOVE_STEP_XY: MovementOrderItem = (ELBOW, SHOULDER)
    MOVE_STEP_Z: MovementOrderItem = (COLUMN, )
    MOVE_STEP_XYZ: MovementOrderItem = (ELBOW, SHOULDER, COLUMN)

    MOVE_Z_XY: MovementOrder = (MOVE_STEP_Z, MOVE_STEP_XY)
    MOVE_XY_Z: MovementOrder = (MOVE_STEP_XY, MOVE_STEP_Z)
    MOVE_XYZ: MovementOrder = (MOVE_STEP_XYZ, )

    def __init__(self, controller: C9Controller=C9Controller.default_controller, column_axis_number: int=3,
                 shoulder_axis_number: int=2, elbow_axis_number: int=1, gripper_axis_number: int=0, probe_offset: float=41.5,
                 gripper_output: int=0, velocity_counts=20_000, acceleration_counts=20_000,
                 elbow_bias: int=C9Controller.BIAS_MIN_SHOULDER, home: bool=False) -> None:

        Robot.__init__(self, controller)

        self.column = PrismaticAxis(controller, column_axis_number, counts_per_mm=100, zero_position_mm=280, inverted=True,
                                    velocity_counts=velocity_counts, acceleration_counts=acceleration_counts)

        self.shoulder = RevoluteAxis(controller, shoulder_axis_number, counts_per_revolution=101_000, zero_position_degrees=-118.87128712871288,
                                     velocity_counts=velocity_counts, acceleration_counts=acceleration_counts,
                                     inverted=True)

        self.elbow = RevoluteAxis(controller, elbow_axis_number, counts_per_revolution=51_000, zero_position_degrees=148.23529411764704,
                                  velocity_counts=velocity_counts, acceleration_counts=acceleration_counts)

        self.gripper = RevoluteAxis(controller, gripper_axis_number, counts_per_revolution=4000, zero_position_degrees=180,
                                    velocity_counts=velocity_counts, acceleration_counts=acceleration_counts)

        self.gripper_output = OpenOutput(controller, gripper_output, open_state=False)
        self.probe_offset = probe_offset
        self.elbow_bias = elbow_bias
        self.velocity_counts = velocity_counts
        self.acceleration_counts = acceleration_counts

        if self.controller.connection.connected:
            self.controller.speed(velocity_counts, acceleration_counts)
            self.controller.elbow_bias(elbow_bias)

            if home:
                self.controller.home()


    @property
    def location(self):
        return Vector3(*self.controller.cartesian_position())

    def home(self):
        self.controller.home(if_needed=True)

    def move(self, x: Optional[float]=None, y: Optional[float]=None, z: Optional[float]=None, gripper: Optional[float]=None,
             velocity: Optional[float]=None, acceleration: Optional[float]=None, relative=False, wait: bool=True, probe: bool=False):

        if probe:
            self.controller.use_probe(True)

        if velocity is None:
            velocity = self.velocity_counts

        if acceleration is None:
            acceleration = self.acceleration_counts

        self.controller.move_arm(x, y, z, gripper, velocity=velocity, acceleration=acceleration, relative=relative, wait=wait)

        if probe:
            self.controller.use_probe(False)

    def move_to_location(self, location: Union[Location, Vector3, Component, list, dict], gripper: Optional[float]=None, order: MovementOrder=MOVE_XYZ,
                         velocity: Optional[float]=None, acceleration: Optional[float]=None, probe: bool=False):
        if isinstance(location, Component):
            position = location.location.position
        elif isinstance(location, list):
            position = Vector3(*location)
        elif isinstance(location, dict):
            position = Vector3(*[location.get(i, 0) for i in ('x', 'y', 'z')])
        elif isinstance(location, Location):
            position = location.position
        else:
            position = location

        kwargs = dict(velocity=velocity, acceleration=acceleration, probe=probe)

        for item in order:
            if item == self.MOVE_STEP_Z:
                self.move(z=position.z(), **kwargs)
            elif item == self.MOVE_STEP_XY:
                self.move(x=position.x(), y=position.y(), gripper=gripper, **kwargs)
            elif item == self.MOVE_STEP_XYZ:
                self.move(x=position.x(), y=position.y(), z=position.z(), gripper=gripper, **kwargs)
            else:
                raise N9RobotMovementInvalidMovementOrder(f'Invalid movement order item: {item}')

    def move_to_locations(self, locations: List[Union[Location, Vector3, Component, list, dict]], gripper: Optional[float]=None, order: MovementOrder=MOVE_XYZ,
                         velocity: Optional[float]=None, acceleration: Optional[float]=None, probe: bool=False):
        for location in locations:
            self.move_to_location(location, gripper=gripper, order=order, velocity=velocity, acceleration=acceleration, probe=probe)