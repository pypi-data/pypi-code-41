__all__ = ["Argument", "ValueArgument", "ListArgument",
           "Bool", "Str", "Path", "Int", "Float",
           "StrList", "PathList", "IntList", "FloatList"]

import re
import os
import argparse
from dataclasses import dataclass
from typing import List, Dict, Tuple, Any, Sequence


@dataclass(frozen=True)
class Argument:
    name: str
    shortcut: str = None
    help: str = None
    required: bool = False

    @property
    def default_value(self):
        return

    def json_schema(self) -> dict:
        schema = {"title": self.name}
        if self.help:
            schema["description"] = self.help
        if self.default_value:
            schema["default"] = self.default_value
        return schema

    def generate_args(self) -> Tuple[List, Dict]:
        args = list()
        if self.shortcut is not None:
            if len(self.shortcut) > 1:
                raise ValueError(f"argument shortcut must be a character: "
                                 f"len({self.shortcut}) > 1")
            if not self.shortcut.isalpha():
                raise ValueError(f"argument shortcut must be an alphabet: "
                                 f"{self.shortcut}")
            args.append(f"-{self.shortcut}")
        args.append(f"--{self.name}")
        kwargs = dict()
        kwargs["help"] = self.help
        kwargs["required"] = self.required
        return args, kwargs


@dataclass(frozen=True)
class Bool(Argument):
    invert: bool = False

    @property
    def default_value(self):
        return self.invert

    def json_schema(self) -> dict:
        return {"type": "boolean"}

    def generate_args(self) -> Tuple[List, Dict]:
        args, kwargs = super(Bool, self).generate_args()
        kwargs["action"] = "store_true" if not self.invert else "store_false"
        kwargs["default"] = self.default_value
        if "required" in kwargs:
            del kwargs["required"]
        default_msg = "(default: False)"
        if "help" in kwargs and kwargs["help"]:
            kwargs["help"] = f"{kwargs['help']} {default_msg}"
        else:
            kwargs["help"] = default_msg
        return args, kwargs


@dataclass(frozen=True)
class ValueArgument(Argument):
    default: Any = None

    @property
    def default_value(self):
        if self.default is not None:
            return self.cast(self.default)

    def validate(self, value) -> bool:
        raise NotImplementedError

    def cast(self, value):
        return value

    def type_cast(self, value):
        if value is None:
            return
        value = self.cast(value)
        if not self.validate(value):
            raise argparse.ArgumentTypeError(f"validation failed: {value}")
        return value

    def generate_args(self) -> Tuple[List, Dict]:
        args, kwargs = super(ValueArgument, self).generate_args()
        kwargs["type"] = self.type_cast
        if self.default is not None:
            kwargs["default"] = self.default_value
            if "help" in kwargs and kwargs["help"]:
                kwargs["help"] = f"{kwargs['help']} (default: %(default)s)"
            else:
                kwargs["help"] = "(default: %(default)s)"
        return args, kwargs


@dataclass(frozen=True)
class Str(ValueArgument):
    choices: Sequence[str] = None
    min_length: int = None
    max_length: int = None
    regex: str = None
    format: str = None

    def cast(self, value):
        return str(value)

    def json_schema(self) -> dict:
        schema = super(Str, self).json_schema()
        schema["type"] = ["string"]
        if not self.required:
            schema["type"].append("null")
        if self.min_length is not None:
            schema["minLength"] = self.min_length
        if self.max_length is not None:
            schema["maxLength"] = self.max_length
        if self.regex is not None:
            schema["pattern"] = self.regex
        if self.format is not None:
            schema["format"] = self.format
        if self.choices is not None:
            schema["enum"] = list(self.choices)
        return schema

    def validate(self, value: str) -> bool:
        if self.regex is not None:
            return re.match(self.regex, value) is not None
        if self.min_length is not None and len(value) < self.min_length:
            return False
        if self.max_length is not None and len(value) > self.max_length:
            return False
        return True

    def generate_args(self) -> Tuple[List, Dict]:
        args, kwargs = super(Str, self).generate_args()
        if self.choices is not None:
            kwargs["choices"] = list(self.choices)
        return args, kwargs


@dataclass(frozen=True)
class Path(ValueArgument):
    must_exist: bool = False
    is_dir: bool = False

    def cast(self, value):
        return os.path.abspath(os.path.realpath(str(value)))

    def validate(self, value) -> bool:
        if self.must_exist and self.is_dir and not os.path.isdir(value):
            return False
        if self.must_exist and not os.path.exists(value):
            return False
        return True

    def json_schema(self) -> dict:
        schema = super(Path, self).json_schema()
        schema["type"] = ["string"]
        if not self.required:
            schema["type"].append("null")
        schema["format"] = "uri"
        return schema

    def generate_args(self) -> Tuple[List, Dict]:
        return super(Path, self).generate_args()


@dataclass(frozen=True)
class Int(ValueArgument):
    min_bound: int = None
    max_bound: int = None
    multiples: int = None
    choices: Sequence[int] = None

    def json_schema(self) -> dict:
        schema = super(Int, self).json_schema()
        schema["type"] = ["integer"]
        if not self.required:
            schema["type"].append("null")
        if self.multiples is not None:
            schema["multipleOf"] = self.multiples
        if self.min_bound is not None:
            schema["minimum"] = self.min_bound
        if self.max_bound is not None:
            schema["exclusiveMaximum"] = self.max_bound
        return schema

    def cast(self, value):
        return int(value)

    def validate(self, value: int) -> bool:
        if self.min_bound is not None and value < self.min_bound:
            return False
        if self.max_bound is not None and value >= self.max_bound:
            return False
        if self.choices is not None and value not in self.choices:
            return False
        if self.multiples is not None and value % self.multiples != 0:
            return False
        return True


@dataclass(frozen=True)
class Float(ValueArgument):
    min_bound: float = None
    max_bound: float = None
    multiples: float = None
    choices: Sequence[float] = None

    def json_schema(self) -> dict:
        schema = super(Float, self).json_schema()
        schema["type"] = ["number"]
        if not self.required:
            schema["type"].append("null")
        if self.multiples is not None:
            schema["multipleOf"] = self.multiples
        if self.min_bound is not None:
            schema["minimum"] = self.min_bound
        if self.max_bound is not None:
            schema["exclusiveMaximum"] = self.max_bound
        return schema

    def cast(self, value):
        return float(value)

    def validate(self, value) -> bool:
        if self.min_bound is not None and value < self.min_bound:
            return False
        if self.max_bound is not None and value >= self.max_bound:
            return False
        if self.choices is not None and value not in self.choices:
            return False
        if self.multiples is not None and value % self.multiples != 0:
            return False
        return True


@dataclass(frozen=True)
class ListArgument(ValueArgument):
    num_elements: int = None

    @property
    def default_value(self):
        if self.default is not None:
            return list(self.default)

    def json_schema(self) -> dict:
        schema = super(ValueArgument, self).json_schema()
        schema["type"] = ["array"]
        if not self.required:
            schema["type"].append("null")
        schema["items"] = super(ListArgument, self).json_schema()
        schema["items"]["title"] = schema["items"]["title"] + "/item"
        return schema

    def generate_args(self) -> Tuple[List, Dict]:
        args, kwargs = super(ListArgument, self).generate_args()
        if self.num_elements is None:
            kwargs["nargs"] = "+" if self.required else "*"
        else:
            kwargs["nargs"] = self.num_elements
        kwargs["default"] = self.default_value
        return args, kwargs

    def validate(self, value) -> bool:
        return super(ListArgument, self).validate(value)


@dataclass(frozen=True)
class StrList(ListArgument, Str):
    pass


@dataclass(frozen=True)
class IntList(ListArgument, Int):
    pass


@dataclass(frozen=True)
class FloatList(ListArgument, Float):
    pass


@dataclass(frozen=True)
class PathList(ListArgument, Path):
    pass