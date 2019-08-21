"""
Author: qiacai
"""
import logging

from ada_core.algorithms import algorithm_meta
from ada_core import exceptions
from ada_core.data_model.io_data_type import AlgorithmIODataType

logger = logging.getLogger(__name__)


class AlgorithmFactory(object):

    _cls_name_list = algorithm_meta.__all__
    logger.info("Initialized the algorithm factory")

    #@classmethod
    def getAlgorithmMeta(self, alg_name, input_type):

        if not alg_name or not isinstance(alg_name, str):
            error_content = "the input val alg_name should be str"
            logger.error(error_content)
            raise exceptions.ParametersNotPassed(error_content)

        if not AlgorithmIODataType.hasType(input_type):
            error_content = "the input val input_type is not valid"
            logger.error(error_content)
            raise exceptions.ParametersNotPassed(error_content)

        alg_meta_class = None

        for cls_name in AlgorithmFactory._cls_name_list:

            cls_class = algorithm_meta.__dict__.get(cls_name)
            if cls_class.alg_name == alg_name and isinstance(cls_class.input_value, input_type):
                alg_meta_class = cls_class
                break
            else:
                continue

        if alg_meta_class is None:
            error_content = 'Could not find algorithm meta class based on name {} and input_type {}'.format(alg_name, str(input_type))
            logger.error(error_content)
            raise exceptions.AlgorithmNotFound(error_content)

        return alg_meta_class

        #@classmethod
    def getAlgorithmMetaList(self, alg_name):

        if not alg_name or not isinstance(alg_name, str):
            error_content = "the input val alg_name should be str"
            logger.error(error_content)
            raise exceptions.ParametersNotPassed(error_content)

        meta_class_list = []

        for cls_name in AlgorithmFactory._cls_name_list:

            cls_class = algorithm_meta.__dict__.get(cls_name)
            if cls_class.alg_name == alg_name:
                meta_class_list.append(cls_class)
            else:
                continue

        if not meta_class_list:
            error_content = 'Could not find algorithm meta class based on name {}'.format(alg_name)
            logger.error(error_content)
            raise exceptions.AlgorithmNotFound(error_content)

        return meta_class_list

    #@classmethod
    def getAlgorithm(self, alg_name, input_type):

        if not alg_name or not isinstance(alg_name, str):
            error_content = "the input val alg_name should be str"
            logger.error(error_content)
            raise exceptions.ParametersNotPassed(error_content)

        if not AlgorithmIODataType.hasType(input_type):
            error_content = "the input val input_type is not valid"
            logger.error(error_content)
            raise exceptions.ParametersNotPassed(error_content)

        alg_cls = None

        for cls_name in AlgorithmFactory._cls_name_list:

            cls_class = algorithm_meta.__dict__.get(cls_name)
            if cls_class.alg_name == alg_name and isinstance(cls_class.input_value, input_type):
                alg_cls = cls_class.alg_cls
                break
            else:
                continue

        if alg_cls is None:
            error_content = 'Could not find algorithm meta class based on name {} and input_type {}'.format(alg_name, str(input_type))
            logger.error(error_content)
            raise exceptions.AlgorithmNotFound(error_content)

        # for alg in AlgorithmFactory._alg_obj_list:
        #     if type(alg) is alg_cls:
        #         return alg
        #     else:
        #         continue

        alg_obj = alg_cls()
        # AlgorithmFactory._alg_obj_list.append(alg_obj)

        return alg_obj

    #@classmethod
    def getAlgorithmOutputType(self, alg_name, input_type):

        if not alg_name or not isinstance(alg_name, str):
            error_content = "the input val alg_name should be str"
            logger.error(error_content)
            raise exceptions.ParametersNotPassed(error_content)

        if not AlgorithmIODataType.hasType(input_type):
            error_content = "the input val input_type is not valid"
            logger.error(error_content)
            raise exceptions.ParametersNotPassed(error_content)

        alg_output_value = None

        for cls_name in AlgorithmFactory._cls_name_list:

            cls_class = algorithm_meta.__dict__.get(cls_name)
            if cls_class.alg_name == alg_name and isinstance(cls_class.input_value,input_type):
                alg_output_value = cls_class.output_value
                break
            else:
                continue

        if alg_output_value is None:
            error_content = 'Could not find algorithm meta class based on name {} and input_type {}'.format(alg_name, str(input_type))
            logger.error(error_content)
            raise exceptions.AlgorithmNotFound(error_content)

        return type(alg_output_value)