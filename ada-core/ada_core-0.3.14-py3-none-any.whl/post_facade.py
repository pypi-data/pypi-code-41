import json
from collections import Mapping
from schematics import Model
from schematics.types import StringType, DictType, BaseType
from schematics.exceptions import ConversionError, BaseError, CompoundError, ValidationError, DataError
from ada_core.data_model.io_data_type import AlgorithmIODataType
from ada_core import exceptions
from ada_core.handler import Handler


class HandlerInputType(BaseType):
    primitive_type = dict
    native_type = dict

    def to_native(self, input_value, context=None):

        strType = StringType()

        def check_simple_input(simple_input):

            if isinstance(simple_input, Mapping) and len(simple_input) == 1 and list(simple_input.keys())[0] in ['handler_call', 'data_entity']:
                try:
                    strType.validate(list(simple_input.values())[0])
                except (ConversionError, DataError):
                    raise ConversionError('The simple input element value should be a str which is a input_data key')

            # if not isinstance(simple_input, Mapping) or len(simple_input) != 1:
            #     raise ConversionError('Only mappings with 1 pair is valid as simple input')
            # else:
            #     if list(simple_input.keys())[0] not in ['handler_call', 'data_entity']:
            #         raise ConversionError('The simple input element key should be handler_call or data_entity')
            #     try:
            #         strType.validate(list(simple_input.values())[0])
            #     except (ConversionError, DataError):
            #         raise ConversionError('The simple input element value should be a str which is a input_data key')

        # if not isinstance(input_value, Mapping) or len(input_value) < 1:
        #     raise ConversionError('Only mappings with at least 1 pair may be used in a TimeSeriesType')

        if not isinstance(input_value, Mapping):
            return input_value
        if len(input_value) == 1:
            try:
                check_simple_input(input_value)
            except ConversionError as exp:
                raise CompoundError({'error': exp})
        else:
            errors = {}
            for key, sub in input_value.items():
                try:
                    check_simple_input(sub)
                except ConversionError as exp:
                    errors[key] = exp
            if errors:
                raise CompoundError(errors)

        return input_value

    def to_primitive(self, input_value, context=None):

        self.to_native(input_value, context)


class HandlerConfigInput(Model):
    algorithm_name = StringType(required=True)
    handler_input = HandlerInputType(required=True)
    algorithm_input_type = StringType(choices=AlgorithmIODataType.getAllTypeName())
    algorithm_output_type = StringType(choices=AlgorithmIODataType.getAllTypeName())
    params = DictType(BaseType, default={})


class PostFacade(object):

    def postHandlerJob(self, json_config, input_data=None):

        # check input_data
        if input_data is not None and not isinstance(input_data, Mapping):
            return exceptions.ParametersNotPassed('The input data is not valid')

        # check json_config
        if json_config is None:
            return exceptions.ParametersNotPassed('The input json_config is not valid')
        if isinstance(json_config, str):
            # todo: add try except
            json_config = json.loads(json_config)
        if not json_config or not isinstance(json_config, Mapping):
            return exceptions.ParametersNotPassed('The input json_config is not valid')

        # todo: currently only parse simple version
        if len(json_config) != 1:
            return exceptions.ParametersNotPassed('The input json_config currently only support simple version')

        # check whether the input fit schema
        handler_config = list(json_config.values())[0]

        try:
            handlerConfig = HandlerConfigInput(handler_config)
            handlerConfig.validate()
        except (CompoundError, ConversionError) as e:
            return exceptions.ParametersNotPassed('The json_config did not pass validation, errors:{}'.format(e))

        handlerConfig = self._parseHandlerInput(input_data, handlerConfig)

        handler = Handler(**handlerConfig)

        return self._parseHandlerOutput(handler)

    def _parseHandlerInput(self, input_data, handlerConfig):

        handler_input = handlerConfig.handler_input

        def parseSimpleInput(input_data, input_config):

            if not isinstance(input_config, Mapping) or len(input_config) != 1 or list(input_config.keys())[0] not in ['handler_call', 'data_entity']:
                return input_config

            # key = list(input_config.keys())[0]
            # if key != 'data_entity': #'The input currently must be data_entity'
            #     return input_config

            data_key = list(input_config.values())[0]
            if input_data is None or not isinstance(input_data, Mapping) or data_key not in input_data.keys():
                raise exceptions.ParametersNotPassed('Could not find the corresponding data')
            return input_data.get(data_key)

        if not isinstance(handler_input, Mapping):
            return handlerConfig
        if len(handler_input) < 1:
            raise exceptions.ParametersNotPassed('The handler_input is not valid')
        elif len(handler_input) == 1:
            parsed_handler_input = parseSimpleInput(input_data, handler_input)

        else:
            parsed_handler_input = {}
            for sub_key, sub in handler_input.items():
                parsed_sub = parseSimpleInput(input_data, sub)
                parsed_handler_input.update({sub_key: parsed_sub})

        handlerConfig.handler_input = parsed_handler_input

        return handlerConfig

    def _parseHandlerOutput(self, handler):

        facade_output = {
            "result": handler.get_result(),
            "extend_info": handler.get_alg_extend_info()
        }

        return facade_output