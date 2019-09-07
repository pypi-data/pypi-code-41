from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils import timezone
from django.utils.translation import ugettext as _
from ohm2_handlers_light.models import BaseModel
from . import managers
from . import settings



"""
class Model(BaseModel):
	pass
"""


class Configuration(BaseModel):
    NETWORK_INTERFACE = 'network_interface'
    NODE_TYPE = 'node_type'
    MASTER_VAL_STATUS = 'master_val_status'
    KEEP_RUNNING_MASTER_VAL = 'keep_running_master_val'
    CURRENT_IRRIGATION_SECTOR = 'current_irrigation_sector'
    BOOL_STOP_IRRIGATION_CONTROL_EVENT = 'bool_stop_irrigation_control_event'
    REASON_STOP_IRRIGATION_CONTROL_EVENT = 'reason_stop_irrigation_control_event'
    ID_BLOCKING_IRRIGATION_EQUIPMENT = 'id_blocking_irrigation_equipment'
    NUMBER_OF_IRRIGATION_SECTOR = 'number_of_irrigation_sector'
    NUMBER_OF_IRRIGATION_SECTOR_WITH_DROPPER_SPILLAGE_MEASURING = 'number_of_irrigation_sector_with_dropper_spillage_measuring'
    key = models.CharField(max_length=settings.STRING_NORMAL, default='')
    value = models.CharField(max_length=settings.STRING_MEDIUM, default='')






