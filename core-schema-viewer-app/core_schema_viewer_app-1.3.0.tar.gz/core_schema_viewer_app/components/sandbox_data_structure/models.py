""" Sandbox Data Structure
"""
from mongoengine import errors as mongoengine_errors

from core_main_app.commons import exceptions as exceptions
from core_parser_app.components.data_structure.models import DataStructure
from core_parser_app.tools.parser import parser
from signals_utils.signals.mongo import connector, signals


class SandboxDataStructure(DataStructure):
    """ Sandbox data structure
    """

    @staticmethod
    def get_by_id(data_structure_id):
        """ Return the object with the given id.

        Args:
            data_structure_id:

        Returns:
            Sandbox Data Structure (obj): SandboxDataStructure object with the given id

        """
        try:
            return SandboxDataStructure.objects.get(pk=str(data_structure_id))
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(str(e))
        except Exception as ex:
            raise exceptions.ModelError(str(ex))

    @staticmethod
    def get_all():
        """ Return all data structures

        Returns:

        """
        return SandboxDataStructure.objects().all()


# Connect signals
connector.connect(DataStructure.pre_delete, signals.pre_delete, SandboxDataStructure)
