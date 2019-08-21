from ..service.tfs_service import TFS_Service

class Factory(object):
    
    @staticmethod
    def create(service_enum):
        instance = TFS_Service(service_enum.value)
        return instance