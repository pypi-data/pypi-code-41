"""
Author: qiacai
"""

import pytz

from schematics.models import Model
from schematics.types import StringType, ModelType
from schematics.exceptions import ConversionError, BaseError, CompoundError, ValidationError

from ada_core import exceptions, utils, constants
from ada_core.data_model.io_data_type import AlgorithmIODataType
from ada_core.algorithms import *

# todo: check import folder, seperate these to different files in a folder

__all__ = ['BoolNaiveAlgorithmMeta', 'NumNaiveAlgorithmMeta', 'TsNaiveAlgorithmMeta', 'EntryNaiveAlgorithmMeta',
           'BoolNOTLogicJudgeAlgorithmMeta', 'BoolANDLogicBinaryJudgeAlgorithmMeta', 'BoolORLogicBinaryJudgeAlgorithmMeta', 'BoolXORLogicBinaryJudgeAlgorithmMeta',
           'NumEqualsBinaryJudgeAlgorithmMeta', 'EntryEqualsBinaryJudgeAlgorithmMeta', 'TsEqualsBinaryJudgeAlgorithmMeta', 'TsNumEqualsBinaryJudgeAlgorithmMeta','EntryNumEqualsBinaryJudgeAlgorithmMeta',
           'NumGreaterThanBinaryJudgeAlgorithmMeta', 'EntryGreaterThanBinaryJudgeAlgorithmMeta', 'TsGreaterThanBinaryJudgeAlgorithmMeta', 'EntryNumGreaterThanBinaryJudgeAlgorithmMeta', 'TsNumGreaterThanBinaryJudgeAlgorithmMeta',
           'NumGreaterThanOrEqualsBinaryJudgeAlgorithmMeta', 'EntryGreaterThanOrEqualsBinaryJudgeAlgorithmMeta', 'TsGreaterThanOrEqualsBinaryJudgeAlgorithmMeta', 'EntryNumGreaterThanOrEqualsBinaryJudgeAlgorithmMeta', 'TsNumGreaterThanOrEqualsBinaryJudgeAlgorithmMeta',
           'NumLessThanBinaryJudgeAlgorithmMeta', 'EntryLessThanBinaryJudgeAlgorithmMeta', 'TsLessThanBinaryJudgeAlgorithmMeta', 'EntryNumLessThanBinaryJudgeAlgorithmMeta', 'TsNumLessThanBinaryJudgeAlgorithmMeta',
           'NumLessThanOrEqualsBinaryJudgeAlgorithmMeta', 'EntryLessThanOrEqualsBinaryJudgeAlgorithmMeta', 'TsLessThanOrEqualsBinaryJudgeAlgorithmMeta', 'EntryNumLessThanOrEqualsBinaryJudgeAlgorithmMeta', 'TsNumLessThanOrEqualsBinaryJudgeAlgorithmMeta',
           'NumValueArithmeticAlgorithmMeta', 'EntryValueArithmeticAlgorithmMeta', 'TsValueArithmeticAlgorithmMeta', 'EntryNumValueArithmeticAlgorithmMeta', 'TsNumValueArithmeticAlgorithmMeta',
           'NumValueComparisonAlgorithmMeta', 'EntryValueComparisonAlgorithmMeta', 'TsValueComparisonAlgorithmMeta', 'EntryNumValueComparisonAlgorithmMeta', 'TsNumValueComparisonAlgorithmMeta',
           'EntryValueFilterAlgorithmMeta', 'EntryNumValueFilterAlgorithmMeta', 'TsValueFilterAlgorithmMeta', 'TsNumValueFilterAlgorithmMeta',
           'NumRoundAlgorithmMeta', 'EntryRoundAlgorithmMeta', 'TsRoundAlgorithmMeta', 'NumAbsAlgorithmMeta', 'EntryAbsAlgorithmMeta', 'TsAbsAlgorithmMeta', 'NumNegAlgorithmMeta', 'EntryNegAlgorithmMeta', 'TsNegAlgorithmMeta',
           'EntryTimeOffsetAlgorithmMeta', 'TsTimeOffsetAlgorithmMeta',
           'TsMeanAlgorithmMeta', 'TsMedianAlgorithmMeta', 'TsMaxAlgorithmMeta', 'TsMinAlgorithmMeta', 'TsCushionAlgorithmMeta','TsPercentileAlgorithmMeta', 'TsStdAlgorithmMeta', 'TsMadAlgorithmMeta', 'TsCountAlgorithmMeta', 'TsSumAlgorithmMeta',
           'TsSplitByTimestampAlgorithmMeta','TsSplitByWindowAlgorithmMeta', 'TsStandardNormalizationAlgorithmMeta',
           'TsScaleNormalizationAlgorithmMeta', 'TsSimpleMovingAverageSmoothingAlgorithmMeta', 'TsExponentialMovingAverageSmoothingAlgorithmMeta', 'TsSeasonalDecomposeAlgorithmMeta', 'TsFilterByPeriodAlgorithmMeta',
           'EntryHardThresholdJudgeAlgorithmMeta', 'TsHardThresholdJudgeAlgorithmMeta', 'NumHardThresholdJudgeAlgorithmMeta',
           'TsSoftThresholdJudgeAlgorithmMeta', 'TsBiSoftThresholdJudgeAlgorithmMeta', 'TsCushionThresholdJudgeAlgorithmMeta', 'TsBiCushionThresholdJudgeAlgorithmMeta'
           ]


class BoolNaiveAlgorithmMeta(Model):
    alg_name = 'naive'
    input_value = AlgorithmIODataType.BOOL.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()
    alg_cls = unary_common_calculate_algorithms.NaiveAlgorithm


class NumNaiveAlgorithmMeta(Model):
    alg_name = 'naive'
    input_value = AlgorithmIODataType.FLOAT.value(required=True)
    output_value = AlgorithmIODataType.FLOAT.value()
    alg_cls = unary_common_calculate_algorithms.NaiveAlgorithm


class TsNaiveAlgorithmMeta(Model):
    alg_name = 'naive'
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.TIME_SERIES.value()
    alg_cls = unary_common_calculate_algorithms.NaiveAlgorithm


class EntryNaiveAlgorithmMeta(Model):
    alg_name = 'naive'
    input_value = AlgorithmIODataType.ENTRY.value(required=True)
    output_value = AlgorithmIODataType.ENTRY.value()
    alg_cls = unary_common_calculate_algorithms.NaiveAlgorithm


class BoolNOTLogicJudgeAlgorithmMeta(Model):
    alg_name = 'not'
    alg_cls = unary_judge_algorithms.NOTLogic
    input_value = AlgorithmIODataType.BOOL.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class BoolANDLogicBinaryJudgeAlgorithmMeta(Model):
    alg_name = 'and'
    alg_cls = binary_judge_algorithms.ANDLogic
    input_value = AlgorithmIODataType.BINARY_BOOL_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class BoolORLogicBinaryJudgeAlgorithmMeta(Model):
    alg_name = 'or'
    alg_cls = binary_judge_algorithms.ORLogic
    input_value = AlgorithmIODataType.BINARY_BOOL_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class BoolXORLogicBinaryJudgeAlgorithmMeta(Model):
    alg_name = 'xor'
    alg_cls = binary_judge_algorithms.XORLogic
    input_value = AlgorithmIODataType.BINARY_BOOL_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class NumEqualsBinaryJudgeAlgorithmMeta(Model):
    alg_name = '=='
    alg_cls = binary_judge_algorithms.Equals
    input_value = AlgorithmIODataType.BINARY_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class EntryEqualsBinaryJudgeAlgorithmMeta(Model):
    alg_name = '=='
    alg_cls = binary_judge_algorithms.Equals
    input_value = AlgorithmIODataType.BINARY_ENTRY_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class TsEqualsBinaryJudgeAlgorithmMeta(Model):
    alg_name = '=='
    alg_cls = binary_judge_algorithms.Equals
    input_value = AlgorithmIODataType.BINARY_TS_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class EntryNumEqualsBinaryJudgeAlgorithmMeta(Model):
    alg_name = '=='
    alg_cls = binary_judge_algorithms.Equals
    input_value = AlgorithmIODataType.BINARY_ENTRY_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class TsNumEqualsBinaryJudgeAlgorithmMeta(Model):
    alg_name = '=='
    alg_cls = binary_judge_algorithms.Equals
    input_value = AlgorithmIODataType.BINARY_TS_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class NumGreaterThanBinaryJudgeAlgorithmMeta(Model):
    alg_name = '>'
    alg_cls = binary_judge_algorithms.GreaterThan
    input_value = AlgorithmIODataType.BINARY_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class EntryGreaterThanBinaryJudgeAlgorithmMeta(Model):
    alg_name = '>'
    alg_cls = binary_judge_algorithms.GreaterThan
    input_value = AlgorithmIODataType.BINARY_ENTRY_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class TsGreaterThanBinaryJudgeAlgorithmMeta(Model):
    alg_name = '>'
    alg_cls = binary_judge_algorithms.GreaterThan
    input_value = AlgorithmIODataType.BINARY_TS_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class EntryNumGreaterThanBinaryJudgeAlgorithmMeta(Model):
    alg_name = '>'
    alg_cls = binary_judge_algorithms.GreaterThan
    input_value = AlgorithmIODataType.BINARY_ENTRY_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class TsNumGreaterThanBinaryJudgeAlgorithmMeta(Model):
    alg_name = '>'
    alg_cls = binary_judge_algorithms.GreaterThan
    input_value = AlgorithmIODataType.BINARY_TS_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class NumGreaterThanOrEqualsBinaryJudgeAlgorithmMeta(Model):
    alg_name = '>='
    alg_cls = binary_judge_algorithms.GreaterThanOrEquals
    input_value = AlgorithmIODataType.BINARY_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class EntryGreaterThanOrEqualsBinaryJudgeAlgorithmMeta(Model):
    alg_name = '>='
    alg_cls = binary_judge_algorithms.GreaterThanOrEquals
    input_value = AlgorithmIODataType.BINARY_ENTRY_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class TsGreaterThanOrEqualsBinaryJudgeAlgorithmMeta(Model):
    alg_name = '>='
    alg_cls = binary_judge_algorithms.GreaterThanOrEquals
    input_value = AlgorithmIODataType.BINARY_TS_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class EntryNumGreaterThanOrEqualsBinaryJudgeAlgorithmMeta(Model):
    alg_name = '>='
    alg_cls = binary_judge_algorithms.GreaterThanOrEquals
    input_value = AlgorithmIODataType.BINARY_ENTRY_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class TsNumGreaterThanOrEqualsBinaryJudgeAlgorithmMeta(Model):
    alg_name = '>='
    alg_cls = binary_judge_algorithms.GreaterThanOrEquals
    input_value = AlgorithmIODataType.BINARY_TS_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class NumLessThanBinaryJudgeAlgorithmMeta(Model):
    alg_name = '<'
    alg_cls = binary_judge_algorithms.LessThan
    input_value = AlgorithmIODataType.BINARY_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class EntryLessThanBinaryJudgeAlgorithmMeta(Model):
    alg_name = '<'
    alg_cls = binary_judge_algorithms.LessThan
    input_value = AlgorithmIODataType.BINARY_ENTRY_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class TsLessThanBinaryJudgeAlgorithmMeta(Model):
    alg_name = '<'
    alg_cls = binary_judge_algorithms.LessThan
    input_value = AlgorithmIODataType.BINARY_TS_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class EntryNumLessThanBinaryJudgeAlgorithmMeta(Model):
    alg_name = '<'
    alg_cls = binary_judge_algorithms.LessThan
    input_value = AlgorithmIODataType.BINARY_ENTRY_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class TsNumLessThanBinaryJudgeAlgorithmMeta(Model):
    alg_name = '<'
    alg_cls = binary_judge_algorithms.LessThan
    input_value = AlgorithmIODataType.BINARY_TS_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class NumLessThanOrEqualsBinaryJudgeAlgorithmMeta(Model):
    alg_name = '<='
    alg_cls = binary_judge_algorithms.LessThanOrEquals
    input_value = AlgorithmIODataType.BINARY_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class EntryLessThanOrEqualsBinaryJudgeAlgorithmMeta(Model):
    alg_name = '<='
    alg_cls = binary_judge_algorithms.LessThanOrEquals
    input_value = AlgorithmIODataType.BINARY_ENTRY_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class TsLessThanOrEqualsBinaryJudgeAlgorithmMeta(Model):
    alg_name = '<='
    alg_cls = binary_judge_algorithms.LessThanOrEquals
    input_value = AlgorithmIODataType.BINARY_TS_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class EntryNumLessThanOrEqualsBinaryJudgeAlgorithmMeta(Model):
    alg_name = '<='
    alg_cls = binary_judge_algorithms.LessThanOrEquals
    input_value = AlgorithmIODataType.BINARY_ENTRY_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class TsNumLessThanOrEqualsBinaryJudgeAlgorithmMeta(Model):
    alg_name = '<='
    alg_cls = binary_judge_algorithms.LessThanOrEquals
    input_value = AlgorithmIODataType.BINARY_TS_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()


class NumValueArithmeticAlgorithmMeta(Model):
    alg_name = 'value_arithmetic'
    alg_cls = binary_calculate_algorithms.ValueArithmetic
    operator = StringType(choices=['+', '-', '*', '/', '//', '%', '**'], required=True)
    fill_value = AlgorithmIODataType.BOOL.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_VALUE_ARITHMETIC_FILL_VALUE)
    input_value = AlgorithmIODataType.BINARY_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.FLOAT.value()


class EntryValueArithmeticAlgorithmMeta(Model):
    alg_name = 'value_arithmetic'
    alg_cls = binary_calculate_algorithms.ValueArithmetic
    operator = StringType(choices=['+', '-', '*', '/', '//', '%', '**'], required=True)
    fill_value = AlgorithmIODataType.BOOL.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_VALUE_ARITHMETIC_FILL_VALUE)
    input_value = AlgorithmIODataType.BINARY_ENTRY_INPUT.value(required=True)
    output_value = AlgorithmIODataType.ENTRY.value()


class TsValueArithmeticAlgorithmMeta(Model):
    alg_name = 'value_arithmetic'
    alg_cls = binary_calculate_algorithms.ValueArithmetic
    operator = StringType(choices=['+', '-', '*', '/', '//', '%'], required=True)
    fill_value = AlgorithmIODataType.BOOL.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_VALUE_ARITHMETIC_FILL_VALUE)
    input_value = AlgorithmIODataType.BINARY_TS_INPUT.value(required=True)
    output_value = AlgorithmIODataType.TIME_SERIES.value()


class EntryNumValueArithmeticAlgorithmMeta(Model):
    alg_name = 'value_arithmetic'
    alg_cls = binary_calculate_algorithms.ValueArithmetic
    operator = StringType(choices=['+', '-', '*', '/', '//', '%', '**'], required=True)
    fill_value = AlgorithmIODataType.BOOL.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_VALUE_ARITHMETIC_FILL_VALUE)
    input_value = AlgorithmIODataType.BINARY_ENTRY_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.ENTRY.value()


class TsNumValueArithmeticAlgorithmMeta(Model):
    alg_name = 'value_arithmetic'
    alg_cls = binary_calculate_algorithms.ValueArithmetic
    operator = StringType(choices=['+', '-', '*', '/', '//', '%', '**'], required=True)
    fill_value = AlgorithmIODataType.BOOL.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_VALUE_ARITHMETIC_FILL_VALUE)
    input_value = AlgorithmIODataType.BINARY_TS_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.TIME_SERIES.value()


class NumValueComparisonAlgorithmMeta(Model):
    alg_name = 'value_comparison'
    alg_cls = binary_calculate_algorithms.ValueComparison
    operator = StringType(choices=['==', '>', '>=', '<', '<='], required=True)
    fill_value = AlgorithmIODataType.BOOL.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_VALUE_COMPARISON_FILL_VALUE)
    input_value = AlgorithmIODataType.BINARY_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.FLOAT.value()


class EntryValueComparisonAlgorithmMeta(Model):
    alg_name = 'value_comparison'
    alg_cls = binary_calculate_algorithms.ValueComparison
    operator = StringType(choices=['==', '>', '>=', '<', '<='], required=True)
    fill_value = AlgorithmIODataType.BOOL.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_VALUE_COMPARISON_FILL_VALUE)
    input_value = AlgorithmIODataType.BINARY_ENTRY_INPUT.value(required=True)
    output_value = AlgorithmIODataType.ENTRY.value()


class TsValueComparisonAlgorithmMeta(Model):
    alg_name = 'value_comparison'
    alg_cls = binary_calculate_algorithms.ValueComparison
    operator = StringType(choices=['==', '>', '>=', '<', '<='], required=True)
    fill_value = AlgorithmIODataType.BOOL.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_VALUE_COMPARISON_FILL_VALUE)
    input_value = AlgorithmIODataType.BINARY_TS_INPUT.value(required=True)
    output_value = AlgorithmIODataType.TIME_SERIES.value()


class EntryNumValueComparisonAlgorithmMeta(Model):
    alg_name = 'value_comparison'
    alg_cls = binary_calculate_algorithms.ValueComparison
    operator = StringType(choices=['==', '>', '>=', '<', '<='], required=True)
    fill_value = AlgorithmIODataType.BOOL.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_VALUE_COMPARISON_FILL_VALUE)
    input_value = AlgorithmIODataType.BINARY_ENTRY_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.ENTRY.value()


class TsNumValueComparisonAlgorithmMeta(Model):
    alg_name = 'value_comparison'
    alg_cls = binary_calculate_algorithms.ValueComparison
    operator = StringType(choices=['==', '>', '>=', '<', '<='], required=True)
    fill_value = AlgorithmIODataType.BOOL.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_VALUE_COMPARISON_FILL_VALUE)
    input_value = AlgorithmIODataType.BINARY_TS_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.TIME_SERIES.value()


class EntryValueFilterAlgorithmMeta(Model):
    alg_name = 'value_filter'
    alg_cls = binary_calculate_algorithms.ValueFilter
    operator = StringType(choices=['==', '>', '>=', '<', '<=', 'mask'], required=True)
    input_value = AlgorithmIODataType.ENTRY.value(required=True)
    output_value = AlgorithmIODataType.ENTRY.value()


class TsValueFilterAlgorithmMeta(Model):
    alg_name = 'value_filter'
    alg_cls = binary_calculate_algorithms.ValueFilter
    operator = StringType(choices=['==', '>', '>=', '<', '<=', 'mask'], required=True)
    input_value = AlgorithmIODataType.BINARY_TS_INPUT.value(required=True)
    output_value = AlgorithmIODataType.TIME_SERIES.value()


class EntryNumValueFilterAlgorithmMeta(Model):
    alg_name = 'value_filter'
    alg_cls = binary_calculate_algorithms.ValueFilter
    operator = StringType(choices=['==', '>', '>=', '<', '<=', 'mask'], required=True)
    input_value = AlgorithmIODataType.BINARY_ENTRY_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.ENTRY.value()


class TsNumValueFilterAlgorithmMeta(Model):
    alg_name = 'value_filter'
    alg_cls = binary_calculate_algorithms.ValueFilter
    operator = StringType(choices=['==', '>', '>=', '<', '<=', 'mask'], required=True)
    input_value = AlgorithmIODataType.BINARY_TS_NUM_INPUT.value(required=True)
    output_value = AlgorithmIODataType.TIME_SERIES.value()


class NumRoundAlgorithmMeta(Model):
    alg_name = 'round'
    alg_cls = unary_common_calculate_algorithms.Round
    ndigits = AlgorithmIODataType.INT.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_ROUND_NDIGITS)
    input_value = AlgorithmIODataType.FLOAT.value(required=True)
    output_value = AlgorithmIODataType.FLOAT.value()


class EntryRoundAlgorithmMeta(Model):
    alg_name = 'round'
    alg_cls = unary_common_calculate_algorithms.Round
    ndigits = AlgorithmIODataType.INT.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_ROUND_NDIGITS)
    input_value = AlgorithmIODataType.ENTRY.value(required=True)
    output_value = AlgorithmIODataType.ENTRY.value()


class TsRoundAlgorithmMeta(Model):
    alg_name = 'round'
    alg_cls = unary_common_calculate_algorithms.Round
    ndigits = AlgorithmIODataType.INT.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_ROUND_NDIGITS)
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.TIME_SERIES.value()


class NumAbsAlgorithmMeta(Model):
    alg_name = 'abs'
    alg_cls = unary_common_calculate_algorithms.Abs
    input_value = AlgorithmIODataType.FLOAT.value(required=True)
    output_value = AlgorithmIODataType.FLOAT.value()


class EntryAbsAlgorithmMeta(Model):
    alg_name = 'abs'
    alg_cls = unary_common_calculate_algorithms.Abs
    input_value = AlgorithmIODataType.ENTRY.value(required=True)
    output_value = AlgorithmIODataType.ENTRY.value()


class TsAbsAlgorithmMeta(Model):
    alg_name = 'abs'
    alg_cls = unary_common_calculate_algorithms.Abs
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.TIME_SERIES.value()


class NumNegAlgorithmMeta(Model):
    alg_name = 'neg'
    alg_cls = unary_common_calculate_algorithms.Neg
    input_value = AlgorithmIODataType.FLOAT.value(required=True)
    output_value = AlgorithmIODataType.FLOAT.value()


class EntryNegAlgorithmMeta(Model):
    alg_name = 'neg'
    alg_cls = unary_common_calculate_algorithms.Neg
    input_value = AlgorithmIODataType.ENTRY.value(required=True)
    output_value = AlgorithmIODataType.ENTRY.value()


class TsNegAlgorithmMeta(Model):
    alg_name = 'neg'
    alg_cls = unary_common_calculate_algorithms.Neg
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.TIME_SERIES.value()


class EntryTimeOffsetAlgorithmMeta(Model):
    alg_name = 'time_offset'
    alg_cls = unary_common_calculate_algorithms.TimeOffset
    offset_window = StringType(default=constants.ALGORITHM_DEFAULT_CALCULATOR_TIME_OFFSET_OFFSET_WINDOW, regex=constants.ALGORITHM_DEFAULT_WINDOW_REGEX)
    timezone = StringType(choices=pytz.all_timezones, default=constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_TIMEZONE)
    input_value = AlgorithmIODataType.ENTRY.value(required=True)
    output_value = AlgorithmIODataType.ENTRY.value()


class TsTimeOffsetAlgorithmMeta(Model):
    alg_name = 'time_offset'
    alg_cls = unary_common_calculate_algorithms.TimeOffset
    offset_window = StringType(default=constants.ALGORITHM_DEFAULT_CALCULATOR_TIME_OFFSET_OFFSET_WINDOW, regex=constants.ALGORITHM_DEFAULT_WINDOW_REGEX)
    timezone = StringType(choices=pytz.all_timezones, default=constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_TIMEZONE)
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.TIME_SERIES.value()


class TsMeanAlgorithmMeta(Model):
    alg_name = 'mean'
    alg_cls = unary_ts2num_calculate_algorithms.Mean
    default = AlgorithmIODataType.FLOAT.value()
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.FLOAT.value()


class TsMedianAlgorithmMeta(Model):
    alg_name = 'median'
    alg_cls = unary_ts2num_calculate_algorithms.Median
    default = AlgorithmIODataType.FLOAT.value()
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.FLOAT.value()


class TsMaxAlgorithmMeta(Model):
    alg_name = 'max'
    alg_cls = unary_ts2num_calculate_algorithms.Max
    default = AlgorithmIODataType.FLOAT.value()
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.FLOAT.value()


class TsMinAlgorithmMeta(Model):
    alg_name = 'min'
    alg_cls = unary_ts2num_calculate_algorithms.Min
    default = AlgorithmIODataType.FLOAT.value()
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.FLOAT.value()


class TsStdAlgorithmMeta(Model):
    alg_name = 'std'
    alg_cls = unary_ts2num_calculate_algorithms.Std
    default = AlgorithmIODataType.FLOAT.value()
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.FLOAT.value()


class TsMadAlgorithmMeta(Model):
    alg_name = 'mad'
    alg_cls = unary_ts2num_calculate_algorithms.Mad
    default = AlgorithmIODataType.FLOAT.value()
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.FLOAT.value()


class TsCountAlgorithmMeta(Model):
    alg_name = 'count'
    alg_cls = unary_ts2num_calculate_algorithms.Count
    default = AlgorithmIODataType.INT.value()
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.INT.value()


class TsSumAlgorithmMeta(Model):
    alg_name = 'sum'
    alg_cls = unary_ts2num_calculate_algorithms.Sum
    default = AlgorithmIODataType.FLOAT.value()
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.FLOAT.value()


class TsPercentileAlgorithmMeta(Model):
    alg_name = 'percentile'
    alg_cls = unary_ts2num_calculate_algorithms.Percentile
    default = AlgorithmIODataType.FLOAT.value()
    percent = AlgorithmIODataType.INT.value(min_value=0, max_value=100, default=constants.ALGORITHM_DEFAULT_CALCULATOR_PERCENTILE_PERCENTILE)
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.FLOAT.value()


class TsCushionAlgorithmMeta(Model):
    alg_name = 'cushion'
    alg_cls = unary_ts2num_calculate_algorithms.Cushion
    default = AlgorithmIODataType.FLOAT.value()
    upper_percentile = AlgorithmIODataType.INT.value(min_value=0, max_value=100)
    lower_percentile = AlgorithmIODataType.INT.value(min_value=0, max_value=100)
    is_upper = AlgorithmIODataType.BOOL.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_CUSHION_IS_UPPER)
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.FLOAT.value()


class TsSplitByTimestampAlgorithmMeta(Model):
    alg_name = 'split_by_timestamp'
    alg_cls = unary_ts2ts_calculate_algorithms.SplitByTimestamp
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    left = AlgorithmIODataType.TIMESTAMP.value(min_value=0)
    left_in_flag = AlgorithmIODataType.BOOL.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_SPLIT_TIMESTAMP_LEFT_IN)
    right = AlgorithmIODataType.TIMESTAMP.value(min_value=0)
    right_in_flag = AlgorithmIODataType.BOOL.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_SPLIT_TIMESTAMP_RIGHT_IN)
    direct = AlgorithmIODataType.BOOL.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_SPLIT_TIMESTAMP_DIRECT)


class TsSplitByWindowAlgorithmMeta(Model):
    alg_name = 'split_by_window'
    alg_cls = unary_ts2ts_calculate_algorithms.SplitByWindow
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    window = StringType(required=True, regex=constants.ALGORITHM_DEFAULT_WINDOW_REGEX)
    timestamp = AlgorithmIODataType.TIMESTAMP.value(min_value=0)
    direct = AlgorithmIODataType.BOOL.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_SPLIT_WINDOW_DIRECT)
    left_in_flag = AlgorithmIODataType.BOOL.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_SPLIT_WINDOW_LEFT_IN)
    right_in_flag = AlgorithmIODataType.BOOL.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_SPLIT_WINDOW_RIGHT_IN)
    timezone = StringType(choices=pytz.all_timezones, default=constants.ALGORITHM_DEFAULT_CALCULATOR_SPLIT_WINDOW_TIMEZONE)


class TsStandardNormalizationAlgorithmMeta(Model):
    alg_name = 'standard_normalization'
    alg_cls = unary_ts2ts_calculate_algorithms.StandardNormalization
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.TIME_SERIES.value()


class TsScaleNormalizationAlgorithmMeta(Model):
    alg_name = 'scale_normalization'
    alg_cls = unary_ts2ts_calculate_algorithms.StandardNormalization
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.TIME_SERIES.value()


class TsSimpleMovingAverageSmoothingAlgorithmMeta(Model):
    alg_name = 'sma_smoothing'
    alg_cls = unary_ts2ts_calculate_algorithms.SimpleMovingAverageSmoothing
    smoothing_window = StringType(default=constants.ALGORITHM_DEFAULT_CALCULATOR_SIMPLE_MA_SMOOTHING_WINDOW, regex=constants.ALGORITHM_DEFAULT_WINDOW_REGEX)
    smoothing_direction = StringType(choices=['forward', 'backward', 'both'], default=constants.ALGORITHM_DEFAULT_CALCULATOR_SIMPLE_MA_SMOOTHING_DIRECTION)
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.TIME_SERIES.value()
    timezone = StringType(choices=pytz.all_timezones, default=constants.ALGORITHM_DEFAULT_CALCULATOR_SIMPLE_MA_TIMEZONE)


class TsExponentialMovingAverageSmoothingAlgorithmMeta(Model):
    alg_name = 'ema_smoothing'
    alg_cls = unary_ts2ts_calculate_algorithms.ExponentialMovingAverageSmoothing
    smoothing_factor = AlgorithmIODataType.FLOAT.value(min_value=0, max_value=1, default=constants.ALGORITHM_DEFAULT_CALCULATOR_EXPONENTIAL_MA_SMOOTHING_FACTOR)
    smoothing_direction = StringType(choices=['forward', 'backward', 'both'], default=constants.ALGORITHM_DEFAULT_CALCULATOR_EXPONENTIAL_MA_SMOOTHING_DIRECTION)
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.TIME_SERIES.value()


class TsSeasonalDecomposeAlgorithmMeta(Model):
    alg_name = 'seasonal_decompose'
    alg_cls = unary_ts2ts_calculate_algorithms.SeasonalDecompose
    period_window = StringType(default=constants.ALGORITHM_DEFAULT_CALCULATOR_SEASONAL_DECOMPOSE_PERIOD_WINDOW, regex=constants.ALGORITHM_DEFAULT_WINDOW_REGEX)
    trend_only = AlgorithmIODataType.BOOL.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_SEASONAL_DECOMPOSE_TREND_ONLY)
    is_fillna = AlgorithmIODataType.BOOL.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_SEASONAL_DECOMPOSE_FILLNA)
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.TIME_SERIES.value()
    timezone = StringType(choices=pytz.all_timezones, default=constants.ALGORITHM_DEFAULT_CALCULATOR_SEASONAL_DECOMPOSE_TIMEZONE)


class TsFilterByPeriodAlgorithmMeta(Model):
    alg_name = 'filter_by_period'
    alg_cls = unary_ts2ts_calculate_algorithms.FilterByPeriod
    period_window = StringType(default=constants.ALGORITHM_DEFAULT_CALCULATOR_FILTER_WITH_PERIOD_PERIOD_WINDOW, regex=constants.ALGORITHM_DEFAULT_WINDOW_REGEX)
    align_point = StringType(default=constants.ALGORITHM_DEFAULT_CALCULATOR_FILTER_WITH_PERIOD_ALIGN_POINT, choices=['start', 'end'])
    direct = AlgorithmIODataType.BOOL.value(default=constants.ALGORITHM_DEFAULT_CALCULATOR_FILTER_WITH_PERIOD_DIRECT)
    timezone = StringType(choices=pytz.all_timezones, default=constants.ALGORITHM_DEFAULT_CALCULATOR_FILTER_WITH_PERIOD_TIMEZONE)
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.TIME_SERIES.value()


class NumHardThresholdJudgeAlgorithmMeta(Model):
    input_value = AlgorithmIODataType.FLOAT.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()
    alg_name = 'hard_threshold'
    alg_cls = unary_judge_algorithms.HardThreshold
    operator = StringType(choices=['>', '>=', '<', '<=', '=='], required=True)
    threshold = AlgorithmIODataType.FLOAT.value(required=True)


class EntryHardThresholdJudgeAlgorithmMeta(Model):
    input_value = AlgorithmIODataType.ENTRY.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()
    alg_name = 'hard_threshold'
    alg_cls = unary_judge_algorithms.HardThreshold
    operator = StringType(choices=['>', '>=', '<', '<=', '=='], required=True)
    threshold = AlgorithmIODataType.FLOAT.value(required=True)


class TsHardThresholdJudgeAlgorithmMeta(Model):
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()
    alg_name = 'hard_threshold'
    alg_cls = unary_judge_algorithms.HardThreshold
    operator = StringType(choices=['>', '>=', '<', '<=', '=='], required=True)
    threshold = AlgorithmIODataType.FLOAT.value(required=True)
    local_window = StringType(default=constants.ALGORITHM_DEFAULT_HARD_THRESHOLD_LOCAL_WINDOW, regex=constants.ALGORITHM_DEFAULT_WINDOW_REGEX)
    timezone = StringType(choices=pytz.all_timezones, default=constants.ALGORITHM_DEFAULT_TIMEZONE)


class TsSoftThresholdJudgeAlgorithmMeta(Model):
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()
    alg_name = 'soft_threshold'
    alg_cls = unary_judge_algorithms.SoftThreshold
    operator = StringType(choices=['>', '>=', '<', '<='], required=True)
    factor = AlgorithmIODataType.FLOAT.value(default=constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_FACTOR, min_value=0)
    local_window = StringType(default=constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_LOCAL_WINDOW, regex=constants.ALGORITHM_DEFAULT_WINDOW_REGEX)
    benchmark_size = StringType(default=constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_BENCHMARK_SIZE, regex=constants.ALGORITHM_DEFAULT_WINDOW_REGEX)
    benchmark_method = StringType(choices=['mean', 'median'], default=constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_BENCHMARK_METHOD)
    bound_method = StringType(choices=['hard', 'std', 'mad', 'ratio'], default=constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_BOUND_METHOD)
    timezone = StringType(choices=pytz.all_timezones, default=constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_TIMEZONE)
    period_window = StringType(default=constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_PERIOD_WINDOW, regex=constants.ALGORITHM_DEFAULT_WINDOW_REGEX)
    period_method = StringType(choices=['filter_by_period', 'seasonal_decompose'], default=constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_PERIOD_METHOD)


class TsBiSoftThresholdJudgeAlgorithmMeta(Model):
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()
    alg_name = 'bi_soft_threshold'
    alg_cls = unary_judge_algorithms.BiSoftThreshold
    enclose = AlgorithmIODataType.BOOL.value(default=constants.ALGORITHM_DEFAULT_BI_SOFT_THRESHOLD_ENCLOSE)
    factor = AlgorithmIODataType.FLOAT.value(default=constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_FACTOR, min_value=0)
    local_window = StringType(default=constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_LOCAL_WINDOW, regex=constants.ALGORITHM_DEFAULT_WINDOW_REGEX)
    benchmark_size = StringType(default=constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_BENCHMARK_SIZE, regex=constants.ALGORITHM_DEFAULT_WINDOW_REGEX)
    benchmark_method = StringType(choices=['mean', 'median'], default=constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_BENCHMARK_METHOD)
    bound_method = StringType(choices=['hard', 'std', 'mad', 'ratio'], default=constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_BOUND_METHOD)
    timezone = StringType(choices=pytz.all_timezones, default=constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_TIMEZONE)
    period_window = StringType(default=constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_PERIOD_WINDOW, regex=constants.ALGORITHM_DEFAULT_WINDOW_REGEX)
    period_method = StringType(choices=['filter_by_period', 'seasonal_decompose'], default=constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_PERIOD_METHOD)


class TsCushionThresholdJudgeAlgorithmMeta(Model):
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()
    alg_name = 'cushion_threshold'
    alg_cls = unary_judge_algorithms.CushionThreshold
    operator = StringType(choices=['>', '>=', '<', '<='], required=True)
    local_window = StringType(default=constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_LOCAL_WINDOW, regex=constants.ALGORITHM_DEFAULT_WINDOW_REGEX)
    benchmark_size = StringType(default=constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_BENCHMARK_SIZE, regex=constants.ALGORITHM_DEFAULT_WINDOW_REGEX)
    benchmark_method = StringType(choices=['mean', 'median'], default=constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_BENCHMARK_METHOD)
    bound_method = StringType(choices=['std', 'mad'], default=constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_BOUND_METHOD)
    factor = AlgorithmIODataType.FLOAT.value(default=constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_FACTOR, min_value=0)
    timezone = StringType(choices=pytz.all_timezones, default=constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_TIMEZONE)
    upper_percentile = AlgorithmIODataType.INT.value(min_value=0, max_value=100)
    lower_percentile = AlgorithmIODataType.INT.value(min_value=0, max_value=100)


class TsBiCushionThresholdJudgeAlgorithmMeta(Model):
    input_value = AlgorithmIODataType.TIME_SERIES.value(required=True)
    output_value = AlgorithmIODataType.BOOL.value()
    alg_name = 'bi_cushion_threshold'
    alg_cls = unary_judge_algorithms.BiCushionThreshold
    enclose = AlgorithmIODataType.BOOL.value(default=constants.ALGORITHM_DEFAULT_BI_CUSHION_THRESHOLD_ENCLOSE)
    local_window = StringType(default=constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_LOCAL_WINDOW, regex=constants.ALGORITHM_DEFAULT_WINDOW_REGEX)
    benchmark_size = StringType(default=constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_BENCHMARK_SIZE, regex=constants.ALGORITHM_DEFAULT_WINDOW_REGEX)
    benchmark_method = StringType(choices=['mean', 'median'], default=constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_BENCHMARK_METHOD)
    bound_method = StringType(choices=['std', 'mad'], default=constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_BOUND_METHOD)
    factor = AlgorithmIODataType.FLOAT.value(default=constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_FACTOR, min_value=0)
    timezone = StringType(choices=pytz.all_timezones, default=constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_TIMEZONE)
    upper_percentile = AlgorithmIODataType.INT.value(min_value=0, max_value=100)
    lower_percentile = AlgorithmIODataType.INT.value(min_value=0, max_value=100)