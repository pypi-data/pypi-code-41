from ..types.validator_status import ValidatorStatus


class SchemaValidator:
    @staticmethod
    def validateSchema(data, config):
        requiredColsNotInData = SchemaValidator.getRequiredColumnsThatArentInData(data, config)
        if len(requiredColsNotInData) > 0:
            message = "Data does not contain the following required columns {}.\nFailing because the remainder of " \
                      "the checks won't be able to complete without this column".format(requiredColsNotInData)
            return ValidatorStatus.FAIL, message
        return ValidatorStatus.SUCCESS, "as"

        # # todo - transition this to pandas
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
