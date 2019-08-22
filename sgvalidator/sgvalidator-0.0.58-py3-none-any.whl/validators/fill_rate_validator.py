from ..types.validator_status import ValidatorStatus
from .validator_utils import ValidatorUtils


class FillRateValidator:
    @staticmethod
    def validateFillRate(series, config):
        percBlank = series.apply(ValidatorUtils.is_missing_or_inaccessible).mean() * 100
        if percBlank >= config.getArgs()["MAXIMIUM_PERC_BLANK_ALLOWED"]:
            message = config.getApology()
            if message is None:
                message = "{}% of column {} is <MISSING> or <INACCESSIBLE>. Are you sure you scraped correctly?"\
                    .format(percBlank, series.name)
            return ValidatorStatus.FAIL, message
        return ValidatorStatus.SUCCESS, None
