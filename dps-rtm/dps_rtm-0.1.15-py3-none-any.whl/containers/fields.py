# --- Standard Library Imports ------------------------------------------------
import collections
from typing import List

# --- Third Party Imports -----------------------------------------------------
import click

# --- Intra-Package Imports ---------------------------------------------------
import rtm.containers.field as ft
import rtm.main.context_managers as context
import rtm.validate.validation as val
from rtm.validate.validator_output import ValidationResult, OutputHeader


class Fields(collections.abc.Sequence):

    # --- Class handling ------------------------------------------------------

    _field_classes = []

    @classmethod
    def get_field_classes(cls):
        return cls._field_classes

    @classmethod
    def append_field(cls, field_class):
        # if not issubclass(field_class, Field):
        #     raise TypeError
        cls._field_classes.append(field_class)

    @classmethod
    def collect_field(cls, collect=True):
        def decorator(field_):
            if collect:  # This is so I can easily switch off the collection of a field
                cls.append_field(field_)
            return field_
        return decorator

    # --- Object handling -----------------------------------------------------

    def __init__(self):
        self.body_length = context.worksheet_columns.get().body_length
        self._fields = [field_class() for field_class in self.get_field_classes()]

    def get_matching_field(self, field_class):
        if isinstance(field_class, str):
            for _field in self:
                if _field.__class__.__name__ == field_class:
                    return _field
        else:
            for _field in self:
                if isinstance(_field, field_class):
                    return _field
        raise ValueError(f'{field_class} not found in {self.__class__}')

    # --- Sequence ------------------------------------------------------------

    def __getitem__(self, item):
        return self._fields[item]

    def __len__(self) -> int:
        return len(self._fields)

    def validate(self):
        # click.echo(self)
        for field_ in self:
            # click.echo(field_.get_name())
            field_.validate()

    def print(self):
        # click.echo(self)
        for field_ in self:
            field_.print()


@Fields.collect_field()
class ID(ft.Field):

    def __init__(self):
        super().__init__("ID")

    def validate(self):
        self._val_results = [
            OutputHeader(self.get_name()),  # Start with header
            val.val_column_exist(self.field_found()),
            val.val_column_sort(self),
        ]


@Fields.collect_field()
class CascadeBlock(ft.Field):
    def __init__(self):
        self._subfields = []
        for subfield_name in self._get_subfield_names():
            subfield = CascadeSubfield(subfield_name)
            if subfield.field_found():
                self._subfields.append(subfield)
            else:
                break

    @staticmethod
    def _get_subfield_names():
        field_names = ["Procedure Step", "User Need", "Design Input"]
        for i in range(1, 20):
            field_names.append("DO Solution L" + str(i))
        return field_names

    def validate(self):
        self._val_results = [
            OutputHeader(self.get_name()),  # Start with header
            val.val_column_exist(self.field_found()),
            val.val_column_sort(self),
            val.val_cascade_block_not_empty(),
            val.val_cascade_block_only_one_entry(),
            val.val_cascade_block_x_or_f(),
            val.val_cascade_block_use_all_columns(),
        ]

    def field_found(self):
        if len(self) > 0:
            return True
        else:
            return False

    def get_body(self):
        return [subfield.get_body() for subfield in self]

    def get_min_index_for_field_right(self):
        if self.field_found():
            return self[-1].get_index()
        else:
            return None

    def get_name(self):
        return 'Cascade Block'

    def get_index(self):
        if self.field_found():
            return self[0].get_index()
        else:
            return None

    def __len__(self):
        return len(self._subfields)

    def __getitem__(self, item):
        return self._subfields[item]


# Not a collected field; rolls up under CascadeBlock
class CascadeSubfield(ft.Field):
    def __init__(self, subfield_name):
        super().__init__(subfield_name)

    def get_name(self):
        return self._name


@Fields.collect_field()
class CascadeLevel(ft.Field):
    def __init__(self):
        super().__init__("Cascade Level")

    def validate(self):

        self._val_results = [
            OutputHeader(self.get_name()),  # Start with header
            val.val_column_exist(self.field_found()),
            val.val_column_sort(self),
            val.val_cells_not_empty(self.get_body()),
            val.valid_cascade_levels(self),
            val.val_matching_cascade_levels(),
        ]


@Fields.collect_field()
class ReqStatement(ft.Field):
    def __init__(self):
        super().__init__("Requirement Statement")

    def validate(self):
        self._val_results = [
            OutputHeader(self.get_name()),  # Start with header
            val.val_column_exist(self.field_found()),
            val.val_column_sort(self),
        ]


@Fields.collect_field()
class ReqRationale(ft.Field):
    def __init__(self):
        super().__init__("Requirement Rationale")

    def validate(self):
        self._val_results = [
            OutputHeader(self.get_name()),  # Start with header
            val.val_column_exist(self.field_found()),
            val.val_column_sort(self),
            val.val_cells_not_empty(self.get_body()),
        ]


@Fields.collect_field()
class VVStrategy(ft.Field):
    def __init__(self):
        super().__init__("Verification or Validation Strategy")

    def validate(self):
        self._val_results = [
            OutputHeader(self.get_name()),  # Start with header
            val.val_column_exist(self.field_found()),
            val.val_column_sort(self),
            val.val_cells_not_empty(self.get_body())
        ]


@Fields.collect_field()
class VVResults(ft.Field):
    def __init__(self):
        super().__init__("Verification or Validation Results")

    def validate(self):
        self._val_results = [
            OutputHeader(self.get_name()),  # Start with header
            val.val_column_exist(self.field_found()),
            val.val_column_sort(self),
        ]


@Fields.collect_field()
class Devices(ft.Field):
    def __init__(self):
        super().__init__("Devices")

    def validate(self):
        self._val_results = [
            OutputHeader(self.get_name()),  # Start with header
            val.val_column_exist(self.field_found()),
            val.val_column_sort(self),
            val.val_cells_not_empty(self.body),
        ]


@Fields.collect_field()
class DOFeatures(ft.Field):
    def __init__(self):
        super().__init__("Design Output Feature (with CTQ ID #)")

    def validate(self):
        self._val_results = [
            OutputHeader(self.get_name()),  # Start with header
            val.val_column_exist(self.field_found()),
            val.val_column_sort(self),
            val.val_cells_not_empty(self.body),
        ]


@Fields.collect_field()
class CTQ(ft.Field):
    def __init__(self):
        super().__init__("CTQ? Yes, No, N/A")

    def validate(self):
        self._val_results = [
            OutputHeader(self.get_name()),  # Start with header
            val.val_column_exist(self.field_found()),
            val.val_column_sort(self),
            val.val_cells_not_empty(self.body),
        ]


if __name__ == "__main__":
    num = 2
    # num = list(range(5))
    if not isinstance(num, collections.abc.Iterable):
        num = [num]
    print(2 in num)
