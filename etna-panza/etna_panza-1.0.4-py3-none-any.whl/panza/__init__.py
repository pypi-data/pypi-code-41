import os.path
import importlib.machinery
from quixote import Blueprint, create_registries


class BlueprintLoadError(Exception):
    """
    Exception class representing an error related to loading a blueprint
    """

    def __init__(self, cause: Exception):
        self.__cause__ = cause

    def __str__(self):
        return f"cannot load blueprint: {str(self.__cause__)}"


class BlueprintLoader:
    @staticmethod
    def load_from_directory(
            directory_path: str,
            blueprint_file_name: str = "blueprint.py",
            complete_load: bool = False
    ) -> Blueprint:
        """
        Load a blueprint from a given directory

        :param directory_path:              the directory containing the blueprint and its resources
        :param blueprint_file_name:         the name of the file to load the blueprint from
        :param complete_load:               whether the additional inspection file should also be loaded (default is False)
        :return:                            the loaded blueprint
        """
        with create_registries() as (builders, fetchers, inspectors):
            path = os.path.join(directory_path, blueprint_file_name)

            try:
                module = importlib.machinery.SourceFileLoader("blueprint", path).load_module()
                blueprint: Blueprint = module.blueprint

                if complete_load is True and blueprint.inspection_file is not None:
                    path = os.path.join(directory_path, blueprint.inspection_file)
                    importlib.machinery.SourceFileLoader("inspection_file", path).load_module()
            except Exception as e:
                raise BlueprintLoadError(e)

            blueprint.register_functions(builders, fetchers, inspectors)

        return blueprint
