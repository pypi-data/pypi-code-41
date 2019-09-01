from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils import timezone
from django.utils.translation import ugettext as _
from ohm2_handlers_light.models import BaseModel
from . import managers
from . import settings
from matialvarezs_charge_controller.github.registers import Value



"""
class Model(BaseModel):
	pass
"""
class LocalDataBackup(BaseModel):
    data = JSONField()
    send_to_server = models.BooleanField(default=True)

class RegistersData(BaseModel):
    address = models.IntegerField(default=0)
    code = models.CharField(default='', max_length=settings.STRING_NORMAL)
    count = models.IntegerField(default=1)
    times = models.IntegerField(default=1)
    unit = models.IntegerField(default=1)
    function_code = models.IntegerField(default=0)
    bits = models.BooleanField(default=False)

    def is_coil(self):
        return self.address < int(0x1000)

    def is_discrete_input(self):
        return self.address >= 0x1000 and self.address < 0x3000
        # return int(str(self.address)) >= int(0x1000) and int(str(self.address)) < int(0x3000)

    def is_input_register(self):
        return self.address >= 0x3000 and self.address < 0x9000

    def is_holding_register(self):
        return self.address >= 0x9000

    def decode(self, response):
        if hasattr(response, "getRegister"):
            mask = rawvalue = lastvalue = 0
            for i in range(self.count):
                lastvalue = response.getRegister(i)
                rawvalue = rawvalue | (lastvalue << (i * 16))
                mask = (mask << 16) | 0xffff
            if (lastvalue & 0x8000) == 0x8000:
                # print rawvalue
                rawvalue = -(rawvalue ^ mask) - 1
            return Value(self, rawvalue)
        # _logger.info("No value for register " + repr(self.name))
        return Value(self, None)

    def decode_bits(self, response):
        if hasattr(response, "bits"):
            return Value(self, response.bits[0])
        # _logger.info("No value for coil " + repr(self.name))
        return Value(self, None)

    def encode(self, value):
        # FIXME handle 2 word registers
        rawvalue = int(value * self.times)
        if rawvalue < 0:
            rawvalue = (-rawvalue - 1) ^ 0xffff
            # print rawvalue
        return rawvalue
