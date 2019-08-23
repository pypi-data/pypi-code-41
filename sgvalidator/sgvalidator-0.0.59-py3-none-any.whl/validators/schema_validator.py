from ..types import *


class SchemaValidator:
    @staticmethod
    def validateSchema(data, config):
        requiredColsNotInData = SchemaValidator.getRequiredColumnsThatArentInData(data, config)
        if len(requiredColsNotInData) > 0:
            message = "Data does not contain the following required columns {}.\nFailing because the remainder of " \
                      "the checks won't be able to complete without this column".format(requiredColsNotInData)
            return ValidatorResponse(ValidatorStatus.FAIL, message)
        return ValidatorResponse(ValidatorStatus.SUCCESS)

        # # todo - do we need this anymore?
        # for row in self.rawData:
        #     for column in row:
        #         if type(row[column]) not in [type(None), type(''), type(u''), type(0), type(0.0), type(True)]:
        #             message = "row {} contains unexpected data type {}".format(row, type(row[column]))
        #             ValidatorUtils.fail(message)
        #             return ValidatorStatus.FAIL
        # return ValidatorStatus.SUCCESS

    @staticmethod
    def getRequiredColumnsThatArentInData(data, config):
        return config.getArgs()["requiredColumns"].difference(data.columns)
