"""
Author: qiacai
"""


from schematics.types import StringType, FloatType, DateTimeType, IntType, NumberType, BooleanType, BaseType, ModelType
from schematics.exceptions import ConversionError, BaseError, CompoundError, ValidationError, DataError
from collections import Mapping
from enum import Enum, unique

from ada_core.data_model.entry import Entry
from ada_core.data_model.time_series import TimeSeries


class EntryType(BaseType):

    primitive_type = dict
    native_type = Entry

    def to_native(self, value, context=None):

        if hasattr(value, "timestamp") and hasattr(value, "value"):
            try:
                data = Entry(int(value.timestamp), float(value.value))
            except (BaseError, ValueError):
                raise ConversionError('timestamp could not convert to int or value could not convert to float')

        elif isinstance(value, tuple):
            if len(value) != 2:
                raise ConversionError("The input tuple should only have 2 elements")
            else:
                try:
                    data = Entry(int(value[0]), float(value[1]))
                except (BaseError, ValueError):
                    raise ConversionError('timestamp could not convert to int or value could not convert to float')

        elif isinstance(value, Mapping):
            if len(value) != 2:
                raise ConversionError("The input dict should only have 2 elements")
            elif not value.get("timestamp") or not value.get("value"):
                raise ConversionError("the input dict should have key 'timestamp' and 'value'")
            else:
                try:
                    data = Entry(int(value.get("timestamp")), float(value.get("value")))
                except (BaseError, ValueError):
                    raise ConversionError('timestamp could not convert to int or value could not convert to float')
        else:
            raise ConversionError('the input could be tuple, dict or other object having attributes: timestamp and value')

        return data

    def to_primitive(self, value, context=None):

        data = self.to_native(value)
        return {"timestamp": data.timestamp, "value": data.value}


class TimeSeriesType(BaseType):

    primitive_type = dict
    native_type = TimeSeries

    def to_native(self, value, context=None):

        if not isinstance(value, Mapping):
            raise ConversionError('Only mappings may be used in a TimeSeriesType')

        data = TimeSeries()
        errors = {}
        for k in sorted(value.keys()):
            try:
                data[int(k)] = float(value.get(k))
            except (BaseError, ValueError) as exc:
                errors[k] = exc
        if errors:
            raise CompoundError(errors)
        return data

    def to_primitive(self, value, context=None):

        if not isinstance(value, Mapping):
            raise ConversionError('Only mappings may be used in a TimeSeriesType')

        data = {}
        errors = {}

        for k in sorted(value.keys()):
            try:
                data[int(k)] = float(value.get(k))
            except (BaseError, ValueError) as exc:
                errors[k] = exc
        if errors:
            raise CompoundError(errors)
        return data


try:

    # @unique
    class BasicDataType(Enum):

        STR = StringType
        FLOAT = FloatType
        INT = IntType
        BOOL = BooleanType
        TIMESTAMP = IntType
        ENTRY = EntryType
        TIME_SERIES = TimeSeriesType

        @classmethod
        def hasType(cls, value):
            return any(value == item.value for item in cls)

        @classmethod
        def hasTypeName(cls, name):
            return any(name == item.name for item in cls)

        @classmethod
        def getType(cls, name):
            nameList = [item.name for item in AlgorithmIODataType]
            valueList = [item.value for item in cls]
            if name in nameList:
                return valueList[nameList.index()]
            else:
                return None

except ValueError as e:
    print(e)

from ada_core.data_model.io_data_model import *


class BinaryBoolInputType(BaseType):

    primitive_type = dict
    native_type = BinaryBoolInput

    def to_native(self, value, context=None):

        if isinstance(value, BinaryBoolInput):
            try:
                value.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryBoolInput value: {}'.format(exp))
            return value

        elif not isinstance(value, Mapping):
            raise ConversionError('Only mappings may be used in a BinaryBoolInputType')

        else:
            data_model = BinaryBoolInput(value)
            try:
                data_model.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryBoolInputType: {}'.format(exp))
            return data_model

    def to_primitive(self, value, context=None):

        if isinstance(value, BinaryBoolInput):
            try:
                value.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryBoolInput value: {}'.format(exp))
            return value.to_primitive()

        elif not isinstance(value, Mapping):
            raise ConversionError('Only mappings may be used in a BinaryBoolInputType')

        else:
            data_model = BinaryBoolInput(value)
            try:
                data_model.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryBoolInputType: {}'.format(exp))
            return data_model.to_primitive()


class BinaryNumInputType(BaseType):

    primitive_type = dict
    native_type = BinaryNumInput

    def to_native(self, value, context=None):

        if isinstance(value, BinaryNumInput):
            try:
                value.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryNumInput value: {}'.format(exp))
            return value

        elif not isinstance(value, Mapping):
            raise ConversionError('Only mappings may be used in a BinaryNumInputType')

        else:
            data_model = BinaryNumInput(value)
            try:
                data_model.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryNumInputType: {}'.format(exp))
            return data_model

    def to_primitive(self, value, context=None):

        if isinstance(value, BinaryNumInput):
            try:
                value.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryNumInput value: {}'.format(exp))
            return value.to_primitive()

        elif not isinstance(value, Mapping):
            raise ConversionError('Only mappings may be used in a BinaryNumInputType')

        else:
            data_model = BinaryNumInput(value)
            try:
                data_model.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryNumInputType: {}'.format(exp))
            return data_model.to_primitive()


class BinaryTsInputType(BaseType):

    primitive_type = dict
    native_type = BinaryTsInput

    def to_native(self, value, context=None):

        if isinstance(value, BinaryTsInput):
            try:
                value.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryTsInput value: {}'.format(exp))
            return value

        elif not isinstance(value, Mapping):
            raise ConversionError('Only mappings may be used in a BinaryTsInputType')

        else:
            data_model = BinaryTsInput(value)
            try:
                data_model.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryTsInputType: {}'.format(exp))
            return data_model

    def to_primitive(self, value, context=None):

        if isinstance(value, BinaryTsInput):
            try:
                value.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryTsInput value: {}'.format(exp))
            return value.to_primitive()

        elif not isinstance(value, Mapping):
            raise ConversionError('Only mappings may be used in a BinaryTsInputType')

        else:
            data_model = BinaryTsInput(value)
            try:
                data_model.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryTsInputType: {}'.format(exp))
            return data_model.to_primitive()


class BinaryEntryInputType(BaseType):

    primitive_type = dict
    native_type = BinaryEntryInput

    def to_native(self, value, context=None):

        if isinstance(value, BinaryEntryInput):
            try:
                value.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryEntryInput value: {}'.format(exp))
            return value

        elif not isinstance(value, Mapping):
            raise ConversionError('Only mappings may be used in a BinaryEntryInputType')

        else:
            data_model = BinaryEntryInput(value)
            try:
                data_model.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryEntryInputType: {}'.format(exp))
            return data_model

    def to_primitive(self, value, context=None):

        if isinstance(value, BinaryEntryInput):
            try:
                value.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryEntryInput value: {}'.format(exp))
            return value.to_primitive()

        elif not isinstance(value, Mapping):
            raise ConversionError('Only mappings may be used in a BinaryEntryInputType')

        else:
            data_model = BinaryEntryInput(value)
            try:
                data_model.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryEntryInputType: {}'.format(exp))
            return data_model.to_primitive()


class BinaryTsNumInputType(BaseType):

    primitive_type = dict
    native_type = BinaryTsNumInput

    def to_native(self, value, context=None):

        if isinstance(value, BinaryTsNumInput):
            try:
                value.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryTsNumInput value: {}'.format(exp))
            return value

        elif not isinstance(value, Mapping):
            raise ConversionError('Only mappings may be used in a BinaryTsNumInputType')

        else:
            data_model = BinaryTsNumInput(value)
            try:
                data_model.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryTsNumInputType: {}'.format(exp))
            return data_model

    def to_primitive(self, value, context=None):

        if isinstance(value, BinaryTsNumInput):
            try:
                value.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryTsInput value: {}'.format(exp))
            return value.to_primitive()

        elif not isinstance(value, Mapping):
            raise ConversionError('Only mappings may be used in a BinaryTsNumberInputType')

        else:
            data_model = BinaryTsNumInput(value)
            try:
                data_model.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryTsNumberInputType: {}'.format(exp))
            return data_model.to_primitive()


class BinaryEntryNumInputType(BaseType):

    primitive_type = dict
    native_type = BinaryEntryNumInput

    def to_native(self, value, context=None):

        if isinstance(value, BinaryEntryNumInput):
            try:
                value.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryEntryNumInput value: {}'.format(exp))
            return value

        elif not isinstance(value, Mapping):
            raise ConversionError('Only mappings may be used in a BinaryEntryNumInputType')

        else:
            data_model = BinaryEntryNumInput(value)
            try:
                data_model.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryEntryNumInputType: {}'.format(exp))
            return data_model

    def to_primitive(self, value, context=None):

        if isinstance(value, BinaryEntryNumInput):
            try:
                value.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryEntryNumInput value: {}'.format(exp))
            return value.to_primitive()

        elif not isinstance(value, Mapping):
            raise ConversionError('Only mappings may be used in a BinaryEntryNumInputType')

        else:
            data_model = BinaryEntryNumInput(value)
            try:
                data_model.validate()
            except (DataError, ConversionError) as exp:
                raise ConversionError('Not validate BinaryEntryNumInputType: {}'.format(exp))
            return data_model.to_primitive()

try:
    # @unique
    class AlgorithmIODataType(Enum):

        STR = BasicDataType.STR.value
        FLOAT = BasicDataType.FLOAT.value
        INT = BasicDataType.INT.value
        BOOL = BasicDataType.BOOL.value
        TIMESTAMP = BasicDataType.TIMESTAMP.value
        ENTRY = BasicDataType.ENTRY.value
        TIME_SERIES = BasicDataType.TIME_SERIES.value
        BINARY_BOOL_INPUT = BinaryBoolInputType
        BINARY_NUM_INPUT = BinaryNumInputType
        BINARY_ENTRY_INPUT = BinaryEntryInputType
        BINARY_TS_INPUT = BinaryTsInputType
        BINARY_ENTRY_NUM_INPUT = BinaryEntryNumInputType
        BINARY_TS_NUM_INPUT = BinaryTsNumInputType

        @classmethod
        def hasType(cls, value):
            return any(value == item.value for item in cls)

        @classmethod
        def hasTypeName(cls, name):
            return any(name == item.name for item in cls)

        @classmethod
        def getAllTypeName(cls):
            return [item.name for item in cls]

        @classmethod
        def getAllType(cls):
            return [item.value for item in cls]

        @classmethod
        def getType(cls, name):
            nameList = [item.name for item in cls]
            valueList = [item.value for item in cls]
            if name in nameList:
                return valueList[nameList.index(name)]
            else:
                return None

        @classmethod
        def getTypeName(cls, value):
            nameList = [item.name for item in cls]
            valueList = [item.value for item in cls]
            if value in valueList:
                return nameList[valueList.index(value)]
            else:
                return None


        @classmethod
        def deduceType(cls, input_value):

            type_validate = False
            input_type = None
            try:
                if not type_validate:
                    boolType = AlgorithmIODataType.BOOL.value()
                    boolType.validate(input_value)
                    type_validate = True
                    return AlgorithmIODataType.BOOL.value
            except (TypeError, BaseError):
                type_validate = False

            try:
                if not type_validate:
                    floatType = AlgorithmIODataType.FLOAT.value()
                    floatType.validate(input_value)
                    type_validate = True
                    return AlgorithmIODataType.FLOAT.value
            except (TypeError, BaseError):
                type_validate = False

            try:
                if not type_validate:
                    entryType = AlgorithmIODataType.ENTRY.value()
                    entryType.validate(input_value)
                    type_validate = True
                    return AlgorithmIODataType.ENTRY.value
            except (TypeError, BaseError):
                type_validate = False

            try:
                if not type_validate:
                    tsType = AlgorithmIODataType.TIME_SERIES.value()
                    tsType.validate(input_value)
                    type_validate = True
                    return AlgorithmIODataType.TIME_SERIES.value
            except (TypeError, BaseError):
                type_validate = False

            try:
                if not type_validate:
                    binaryBoolType = AlgorithmIODataType.BINARY_BOOL_INPUT.value()
                    binaryBoolType.validate(input_value)
                    type_validate = True
                    return AlgorithmIODataType.BINARY_BOOL_INPUT.value
            except (TypeError, BaseError):
                type_validate = False

            try:
                if not type_validate:
                    binaryNumType = AlgorithmIODataType.BINARY_NUM_INPUT.value()
                    binaryNumType.validate(input_value)
                    type_validate = True
                    return AlgorithmIODataType.BINARY_NUM_INPUT.value
            except (TypeError, BaseError):
                type_validate = False

            try:
                if not type_validate:
                    binaryEntryType = AlgorithmIODataType.BINARY_ENTRY_INPUT.value()
                    binaryEntryType.validate(input_value)
                    type_validate = True
                    return AlgorithmIODataType.BINARY_ENTRY_INPUT.value
            except (TypeError, BaseError):
                type_validate = False

            try:
                if not type_validate:
                    binaryTsType = AlgorithmIODataType.BINARY_TS_INPUT.value()
                    binaryTsType.validate(input_value)
                    type_validate = True
                    return AlgorithmIODataType.BINARY_TS_INPUT.value
            except (TypeError, BaseError):
                type_validate = False

            try:
                if not type_validate:
                    binaryEntryNumType = AlgorithmIODataType.BINARY_ENTRY_NUM_INPUT.value()
                    binaryEntryNumType.validate(input_value)
                    type_validate = True
                    return AlgorithmIODataType.BINARY_ENTRY_NUM_INPUT.value
            except (TypeError, BaseError):
                type_validate = False

            try:
                if not type_validate:
                    binaryTsNumType = AlgorithmIODataType.BINARY_TS_NUM_INPUT.value()
                    binaryTsNumType.validate(input_value)
                    type_validate = True
                    return AlgorithmIODataType.BINARY_TS_NUM_INPUT.value
            except (TypeError, BaseError):
                type_validate = False

            if not type_validate:
                raise ValueError("could not deduce a valid data type")

            return input_type


except ValueError as e:
    print(e)