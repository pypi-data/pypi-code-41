# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from .exceptions.motion_lib_exception import MotionLibException
from .exceptions.request_timeout_exception import RequestTimeoutException
from .exceptions.connection_closed_exception import ConnectionClosedException
from .exceptions.invalid_argument_exception import InvalidArgumentException
from .exceptions.out_of_request_ids_exception import OutOfRequestIdsException
from .exceptions.invalid_packet_exception import InvalidPacketException
from .exceptions.connection_failed_exception import ConnectionFailedException
from .exceptions.unknown_request_exception import UnknownRequestException
from .exceptions.command_failed_exception import CommandFailedException
from .exceptions.device_db_failed_exception import DeviceDbFailedException
from .exceptions.invalid_data_exception import InvalidDataException
from .exceptions.device_not_identified_exception import DeviceNotIdentifiedException
from .exceptions.conversion_failed_exception import ConversionFailedException
from .exceptions.device_number_conflict_exception import DeviceNumberConflictException
from .exceptions.no_device_found_exception import NoDeviceFoundException
from .exceptions.movement_interrupted_exception import MovementInterruptedException
from .exceptions.movement_failed_exception import MovementFailedException
from .exceptions.io_failed_exception import IoFailedException
from .exceptions.invalid_response_exception import InvalidResponseException
from .exceptions.not_supported_exception import NotSupportedException
from .exceptions.device_failed_exception import DeviceFailedException
from .exceptions.os_failed_exception import OsFailedException
from .exceptions.internal_error_exception import InternalErrorException
from .exceptions.binary_error_exception import BinaryErrorException
from .exceptions.binary_command_failed_exception import BinaryCommandFailedException
from .exceptions.command_preempted_exception import CommandPreemptedException
from .exceptions.lockstep_not_enabled_exception import LockstepNotEnabledException
from .exceptions.lockstep_enabled_exception import LockstepEnabledException
from .exceptions.io_channel_out_of_range_exception import IoChannelOutOfRangeException
from .exceptions.setting_not_found_exception import SettingNotFoundException

errorMap = {
    "REQUEST_TIMEOUT": RequestTimeoutException,
    "CONNECTION_CLOSED": ConnectionClosedException,
    "INVALID_ARGUMENT": InvalidArgumentException,
    "OUT_OF_REQUEST_IDS": OutOfRequestIdsException,
    "INVALID_PACKET": InvalidPacketException,
    "CONNECTION_FAILED": ConnectionFailedException,
    "UNKNOWN_REQUEST": UnknownRequestException,
    "COMMAND_FAILED": CommandFailedException,
    "DEVICE_DB_FAILED": DeviceDbFailedException,
    "INVALID_DATA": InvalidDataException,
    "DEVICE_NOT_IDENTIFIED": DeviceNotIdentifiedException,
    "CONVERSION_FAILED": ConversionFailedException,
    "DEVICE_NUMBER_CONFLICT": DeviceNumberConflictException,
    "NO_DEVICE_FOUND": NoDeviceFoundException,
    "MOVEMENT_INTERRUPTED": MovementInterruptedException,
    "MOVEMENT_FAILED": MovementFailedException,
    "IO_FAILED": IoFailedException,
    "INVALID_RESPONSE": InvalidResponseException,
    "NOT_SUPPORTED": NotSupportedException,
    "DEVICE_FAILED": DeviceFailedException,
    "OS_FAILED": OsFailedException,
    "INTERNAL_ERROR": InternalErrorException,
    "BINARY_ERROR": BinaryErrorException,
    "BINARY_COMMAND_FAILED": BinaryCommandFailedException,
    "COMMAND_PREEMPTED": CommandPreemptedException,
    "LOCKSTEP_NOT_ENABLED": LockstepNotEnabledException,
    "LOCKSTEP_ENABLED": LockstepEnabledException,
    "IO_CHANNEL_OUT_OF_RANGE": IoChannelOutOfRangeException,
    "SETTING_NOT_FOUND": SettingNotFoundException,
}


def convert_exception(error: str, message: str) -> MotionLibException:
    return errorMap[error](message)
