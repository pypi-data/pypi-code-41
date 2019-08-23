"""
    Persistence Adaptor Module
"""
from AuditModule.common import AppConfigurations
from AuditModule.core.persistences.adaptors import CassandraPersistenceAdaptor

#  Register New Adaptors Here
all_registered_adaptors = {"cassandra": CassandraPersistenceAdaptor}


def get_instance(app_module):
    """
    This method the instance of the app module from the corresponding registered adaptor
    :param app_module:
    :return:
    """
    if AppConfigurations.persistence_adaptor not in all_registered_adaptors:
        raise Exception("No registered persistence Adaptor for {}".format(AppConfigurations.persistence_adaptor))
    given_adaptor = all_registered_adaptors[AppConfigurations.persistence_adaptor]
    return getattr(given_adaptor, app_module)()