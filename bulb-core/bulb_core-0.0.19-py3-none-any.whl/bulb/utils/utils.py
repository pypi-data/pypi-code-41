# import bulb
from django.conf import settings
import importlib.util
import os

BASE_DIR = settings.BASE_DIR


def get_folders_paths_list(folders_name):
    """
    This function returns the list of paths of all the folders named with the 'folders_name' value.
    """
    folders_paths = []

    # First, search into the project.
    for root, dirs, files in os.walk(BASE_DIR):
        if folders_name in dirs:
            folders_paths.append(os.path.join(root, folders_name))

    # Then, into the bulb source files.
    # for root, dirs, files in os.walk(bulb.__path__[0]):
    for root, dirs, files in os.walk("/home/liliancruanes/grasse_mat/website/env_grasse_mat_project/lib/python3.7/site-packages/bulb"):
        if folders_name in dirs:
            folders_paths.append(os.path.join(root, folders_name))

    if len(folders_paths) == 0:
        return None

    elif len(folders_paths) == 1:
        return folders_paths[0]

    return folders_paths


def get_files_paths_list(files_name, from_project=True, from_BULB=True):
    """
    This function returns the list of paths of all the folders named with the 'folders_name' value.
    """
    files_paths = []

    # First, search into the project.
    if from_project is True:
        for root, dirs, files in os.walk(BASE_DIR):
            if files_name in files:
                files_paths.append(os.path.join(root, files_name))

    # Then, into the bulb source files.
    if from_BULB is True:
        # for root, dirs, files in os.walk(bulb.__path__[0]):
        for root, dirs, files in os.walk("/home/liliancruanes/grasse_mat/website/env_grasse_mat_project/lib/python3.7/site-packages/bulb"):
            if files_name in files:
                # Exclude the db node_models.
                if not "bulb/db" in root:
                    files_paths.append(os.path.join(root, files_name))

    if len(files_paths) == 0:
        return None

    elif len(files_paths) == 1:
        return files_paths[0]

    return files_paths


def get_all_node_models():
    """
    This function returns the list of all the node_models of the project. It cares about inheritance and overloading.
    """
    from bulb.db.node_models import Node
    node_models_list = []

    for file_path in get_files_paths_list("node_models.py"):

        # Import the module from his path
        spec = importlib.util.spec_from_file_location("node_models", file_path)
        node_models = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(node_models)

        # Get all the module classes that have in their parents the Node class.
        node_model_dict = node_models.__dict__

        for k, v in node_model_dict.items():
            try:
                # Explanation : __module__ return only the name of the module where is contained the node_class (here :
                # "node_models"), but if the node_class is an import, __module__ return the full module path (example :
                # "bulb.contrib.sessions.node_models"). So, this line prevent the detection of the imported
                # classes in the node_models files.
                if Node in v.__mro__ and v.__module__ == "node_models":
                    node_models_list.append(v)
            except:
                pass

        # Allow overloaded native classes.
        Permission_classes = []
        Group_classes = []
        User_classes = []
        Session_classes = []
        for node_model in node_models_list:
            if node_model.__name__ == "Permission":
                Permission_classes.append(node_model)

            elif node_model.__name__ == "Group":
                Group_classes.append(node_model)

            elif node_model.__name__ == "User":
                User_classes.append(node_model)

            elif node_model.__name__ == "Session":
                Session_classes.append(node_model)

        for collected_classes in [Permission_classes, Group_classes, User_classes, Session_classes]:
            if len(collected_classes) > 1:
                selected_class = None
                for collected_class in collected_classes:
                    if selected_class is not None:
                        if len(collected_class.__mro__) >= len(selected_class.__mro__):
                            selected_class = collected_class

                    else:
                        selected_class = collected_class
                collected_classes.remove(selected_class)

                to_remove_classes = collected_classes

                for to_remove_class in to_remove_classes:
                    node_models_list.remove(to_remove_class)

    return node_models_list