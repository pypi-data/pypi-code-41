from ..service.clockify_service import Clockify_Service

class Factory(object):
    
    @staticmethod
    def create(service_enum):
        instance = Clockify_Service(service_enum.value)
        return instance