from typing import List, Union, Callable, Optional, Dict
import time
from north_utils.joystick import Joystick
from north_c9.controller import C9Controller
from north_c9.joysticks import N9Joystick


class Keyframe:
    def __init__(self, x: Optional[float]=None, y: Optional[float]=None, z: Optional[float]=None, gripper: Optional[float]=None):
        self.x = x
        self.y = y
        self.z = z
        self.gripper = gripper

    def move_to(self, controller: C9Controller, **kwargs) -> None:
        controller.move_arm(x=self.x, y=self.y, z=self.z, gripper=self.gripper, **kwargs)


class Sequence:
    sequences: List['Sequence'] = []
    keyframes: List[Optional[Keyframe]] = []

    def __init__(self):
        self.current_index: int = 0
        self.playing = False
        self.paused = False

    @property
    def current_keyframe(self) -> Optional[Keyframe]:
        if len(self.keyframes) <= 0:
            return None

        return self.keyframes[self.current_index]

    def move_to_keyframe(self, controller: C9Controller, keyframe: Optional[Keyframe], **kwargs):
        if keyframe is None:
            return

        controller.move_arm(x=keyframe.x, y=keyframe.y, z=keyframe.z, gripper=keyframe.gripper, **kwargs)

    def move_to_current_keyframe(self, controller: C9Controller, **kwargs):
        self.move_to_keyframe(controller, keyframe=self.current_keyframe, **kwargs)

    def keyframe_step(self, controller: C9Controller, direction: int=1, **kwargs):
        self.current_index += direction

        if self.current_index >= len(self.keyframes):
            self.current_index = len(self.keyframes) - 1
            self.paused = True

        if self.current_index < 0:
            self.current_index = 0
            self.paused = True

        self.move_to_current_keyframe(controller, **kwargs)

    def move_to_next_keyframe(self, controller: C9Controller, **kwargs):
        self.keyframe_step(controller, direction=1, **kwargs)

    def move_to_previous_keyframe(self, controller: C9Controller, **kwargs):
        self.keyframe_step(controller, direction=-1, **kwargs)

    def insert_keyframe(self, keyframe: Keyframe):
        self.keyframes.insert(self.current_index, keyframe)
        self.current_index += 1

    def play(self, controller: C9Controller):
        self.playing = True
        self.move_to_current_keyframe(controller)
        while self.playing:
            if not self.paused:
                self.keyframe_step(controller)

            time.sleep(0.01)


class SequenceBuilder(N9Joystick):
    def __init__(self, controller: C9Controller, sequence: Optional[Sequence]=None):
        self.sequence = sequence if sequence is not None else Sequence()
        self.playback_mode = False
        N9Joystick.__init__(self, controller, moving=True)

    def start(self):
        N9Joystick.start(self)
        self.sequence.paused = True
        self.sequence.play(self.controller)

    def on_record_button(self, pressed: bool):
        if pressed and self.sequence.paused:
            x, y, z = self.controller.cartesian_position()
            gripper = self.controller.axis_position(self.GRIPPER_AXIS, units=True)
            keyframe = Keyframe(x=x, y=y, z=z, gripper=gripper)
            self.sequence.insert_keyframe(keyframe)

    def on_stop_button(self, pressed: bool):
        N9Joystick.on_stop_button(self, pressed)

        if pressed:
            self.sequence.paused = not self.sequence.paused

    def on_playback_mode_button(self, pressed: bool):
        self.playback_mode = pressed

    def on_keyframe_x_axis(self, value: float):
        if value < 0:
            self.sequence.move_to_previous_keyframe(self.controller)
        elif value > 0:
            self.sequence.move_to_next_keyframe(self.controller)

    def on_precise_x_axis_map(self, value: float):
        if not self.playback_mode:
            N9Joystick.on_x_precise_axis(self, value)
        else:
            self.on_keyframe_x_axis(value)

    def on_precise_y_axis_map(self, value: float):
        if not self.playback_mode:
            N9Joystick.on_y_precise_axis(self, value)

    mappings = {
        **N9Joystick.mappings,
        Joystick.RECORD_BUTTON: on_record_button,
        Joystick.STOP_BUTTON: on_stop_button,
        Joystick.PLAYBACK_MODE_BUTTON: on_playback_mode_button,
        Joystick.PRECISE_X_AXIS: on_precise_x_axis_map,
        Joystick.PRECISE_Y_AXIS: on_precise_y_axis_map,
    }
