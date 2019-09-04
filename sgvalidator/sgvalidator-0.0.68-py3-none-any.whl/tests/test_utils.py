from ..config import validators
from ..validator_config import ValidatorConfig


def getMethodAndValidatorConfigFromName(name):
    parsed = [ValidatorConfig().parse(validator) for validator in validators]
    conf = list(filter(lambda x: x.getName() == name, parsed))[0]
    return conf.getMethod(), conf
