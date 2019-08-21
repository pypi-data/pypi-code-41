from schematics import Model
from ada_core.data_model.io_data_type import BasicDataType


class BinaryBoolInput(Model):
    left = BasicDataType.BOOL.value(required=True)
    right = BasicDataType.BOOL.value(required=True)


class BinaryNumInput(Model):
    left = BasicDataType.FLOAT.value(required=True)
    right = BasicDataType.FLOAT.value(required=True)


class BinaryEntryInput(Model):
    left = BasicDataType.ENTRY.value(required=True)
    right = BasicDataType.ENTRY.value(required=True)


class BinaryTsInput(Model):
    left = BasicDataType.TIME_SERIES.value(required=True)
    right = BasicDataType.TIME_SERIES.value(required=True)


class BinaryTsNumInput(Model):
    left = BasicDataType.TIME_SERIES.value(required=True)
    right = BasicDataType.FLOAT.value(required=True)


class BinaryEntryNumInput(Model):
    left = BasicDataType.ENTRY.value(required=True)
    right = BasicDataType.FLOAT.value(required=True)