#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""dataclasses to hold and describe information of flow objects"""

import functools
import time
from abc import ABC
from dataclasses import dataclass, asdict, field, fields, is_dataclass

from ujotypes import UjoBase
from ujotypes.variants.none import UJO_VARIANT_NONE

from titanfe.utils import create_uid, ns_to_ms, time_delta_in_ms
from titanfe.messages import PacketMessage


class DictConvertable(ABC):
    """Mixin to make a dataclass convert from/into a dictionary"""

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, _dict):
        instance = cls(**_dict)
        dicts_to_dataclasses(instance)
        return instance

    def __str__(self):
        return str(self.to_dict())


@dataclass(unsafe_hash=True, frozen=True)
class Brick(DictConvertable):
    """Describes a "Brick" (flow component)"""

    flow: str = "FlowName?"
    name: str = "BrickName?"
    module: str = "Module?"
    inlet: bool = False
    uid: str = field(default_factory=functools.partial(create_uid, "B-"))

    @classmethod
    def from_config(cls, flow_name, brick_config, root_path):
        return cls(
            flow=flow_name,
            name=brick_config["Name"],
            module=str(root_path / brick_config["Module"]),
        )


@dataclass
class Packet(DictConvertable):
    """Represents an information packet (IP) passing through a flow"""

    payload: UjoBase = UJO_VARIANT_NONE
    uid: str = field(default_factory=functools.partial(create_uid, "P-"))
    started: float = field(default_factory=time.time_ns)
    # ancestors: list = field(default_factory=list)
    input_entry: float = 0.0
    input_exit: float = 0.0
    output_entry: float = 0.0
    output_exit: float = 0.0

    @property
    def traveling_time(self) -> float:
        return time_delta_in_ms(self.started)

    @property
    def queue_times(self):
        return {
            "time_in_input": ns_to_ms(self.input_exit - self.input_entry),
            "time_in_output": ns_to_ms(self.output_exit - self.output_entry),
            "time_on_wire": ns_to_ms(self.input_entry - self.output_exit),
        }

    def update_input_entry(self):
        self.input_entry = time.time_ns()

    def update_input_exit(self):
        self.input_exit = time.time_ns()

    def update_output_entry(self):
        self.output_entry = time.time_ns()

    def update_output_exit(self):
        self.output_exit = time.time_ns()

    def as_message(self):
        return PacketMessage(self.to_dict())


def dicts_to_dataclasses(dataclass_instance):
    """Convert all fields of type `dataclass` into an dataclass instance of the
       fields specified dataclass if the current value is of type dict."""
    cls = type(dataclass_instance)
    for data_field in fields(cls):
        if not is_dataclass(data_field.type):
            continue

        value = getattr(dataclass_instance, data_field.name)
        if not isinstance(value, dict):
            continue

        new_value = data_field.type(**value)
        dicts_to_dataclasses(new_value)
        setattr(dataclass_instance, data_field.name, new_value)
