"""
Create an API to get algorithms with Meta Info
"""
import json
import logging

from ada_core import exceptions
from ada_core.data_model.io_data_type import AlgorithmIODataType
from ada_core.algorithms.algorithm_factory import AlgorithmFactory

logger = logging.getLogger(__name__)


class GetFacade(object):

    algorithm_factory = AlgorithmFactory()

    def getAlgorithmMeta(self, algorithm_name, input_type_str=None):

        meta_list = []

        try:
            if input_type_str is None or str(input_type_str) == '':
                cls_list = self.algorithm_factory.getAlgorithmMetaList(algorithm_name)
            else:
                input_type = AlgorithmIODataType.getType(input_type_str)
                if input_type is None:
                    raise exceptions.ParametersNotPassed("the input_type is invalid")

                cls_list = [self.algorithm_factory.getAlgorithmMeta(algorithm_name, input_type)]

        except exceptions.ParametersNotPassed as exp:
            logger.error(exp)
            raise exceptions.AlgorithmNotFound(exp)
            # return {'Error Message': 'could not found algorithm based on name'}

        for cls in cls_list:
            alg_meta_dict = {}
            params = {}
            if cls.alg_name != algorithm_name:
                log_content = 'The returned class is not valid with unmatch alg_name'
                logging.error(log_content)
                raise ValueError(log_content)
                # return {'Error Message': 'The returned class is not valid with unmatch alg_name'}

            alg_meta_dict.update({'alg_name': cls.alg_name})

            for field_name, field_info in cls.fields.items():
                if field_name in ['alg_name', 'input_value', 'output_value']:
                    alg_meta_dict.update({
                        field_name: {
                            "data_type": AlgorithmIODataType.getTypeName(field_info.typeclass),
                            "required": field_info.required if hasattr(field_info, 'required') else None,
                            "max_value": field_info.max_value if hasattr(field_info, 'max_value') else None,
                            "min_value": field_info.min_value if hasattr(field_info, 'min_value') else None,
                            "default": field_info.default if hasattr(field_info, 'default') and str(field_info.default) != 'Undefined' else None,
                            "choices": field_info.choices if hasattr(field_info, 'choices') else None,
                            "regex": field_info.regex.pattern if hasattr(field_info, 'regex') and hasattr(field_info.regex, 'pattern') else None
                        }
                    })
                else:
                    params.update({
                        field_name: {
                            "data_type": AlgorithmIODataType.getTypeName(field_info.typeclass),
                            "required": field_info.required if hasattr(field_info, 'required') else None,
                            "max_value": field_info.max_value if hasattr(field_info, 'max_value') else None,
                            "min_value": field_info.min_value if hasattr(field_info, 'min_value') else None,
                            "default": field_info.default if hasattr(field_info, 'default') and str(field_info.default) != 'Undefined' else None,
                            "choices": field_info.choices if hasattr(field_info, 'choices') else None,
                            "regex": field_info.regex.pattern if hasattr(field_info, 'regex') and hasattr(field_info.regex, 'pattern') else None
                        }
                    })
            alg_meta_dict.update({"params": params})
            meta_list.append(alg_meta_dict)
        meta_info = {"algorithm_meta": meta_list}
        # todo: think about change to return a json, check whether python has ability to remind return type
        #meta_info = json.dumps(meta_info)

        return meta_info
