from enum import Enum


class ConfirmationStatus(Enum):
    CONFIRMED = "Confirmed"
    ALL = "All"


class MessageType(Enum):
    ACTIVATION_SERVICE_NUMBER_V1 = "activationsn"
    CANCEL_V1 = "cancel"
    CONFIRMATION_V1 = "confirmations"
    DEACTIVATION_V1 = "deactivation"
    DEACTIVATION_SERVICE_NUMBER_V1 = "deactivationsn"
    ERROR_FOUND_V1 = "errorfound"
    ENUM_ACTIVATION_NUMBER_V1 = "enumactivationnumber"
    ENUM_ACTIVATION_OPERATOR_V1 = "enumactivationoperator"
    ENUM_ACTIVATION_RANGE_V1 = "enumactivationrange"
    ENUM_DEACTIVATION_NUMBER_V1 = "enumdeactivationnumber"
    ENUM_DEACTIVATION_OPERATOR_V1 = "enumdeactivationoperator"
    ENUM_DEACTIVATION_RANGE_V1 = "enumdeactivationrange"
    ENUM_PROFILE_ACTIVATION_V1 = "enumprofileactivation"
    ENUM_PROFILE_DEACTIVATION_V1 = "enumprofiledeactivation"
    PORTING_REQUEST_V1 = "portingrequest"
    PORTING_REQUEST_ANSWER_V1 = "portingrequestanswer"
    PORTING_PERFORMED_V1 = "portingperformed"
    PORTING_REQUEST_ANSWER_DELAYED_V1 = "pradelayed"
    RANGE_ACTIVATION_V1 = "rangeactivation"
    RANGE_DEACTIVATION_V1 = "rangedeactivation"
    TARIFF_CHANGE_SERVICE_NUMBER_V1 = "tariffchangesn"
    _VERSION_SUFFIX_V1 = "-v1"

    def get_event_type(self):
        return f'{self.value}{self._VERSION_SUFFIX_V1.value}'
