from bulb.contrib.auth.decorators import login_required, staff_only
from bulb.utils import get_files_paths_list, get_all_node_models
from bulb.contrib.handling.exceptions import BULBAdminError
from bulb.contrib.auth.node_models import User
from bulb.db import gdbh
from django.contrib.messages import add_message, SUCCESS, ERROR
from django.shortcuts import render, redirect
from collections import OrderedDict
from django.conf import settings
import importlib.util
import datetime
import json

login_page_url = "/" + settings.BULB_ADMIN_BASEPATH_NAME + "/login"


def get_admin_preview_fields(node_model_name):
    """
    This function return the _preview_fields dictionary of an instance if there is one, else it return None.
    First it tries to find the related dictionary into the project. If it isn't found, it tries to find the dictionary into
    bulb natives files.

    :param node_model_name:
    :return:
    """
    found_preview_fields_list = []

    # Try to find the related admin_preview_fields dict into the project folders and into bulb.
    node_models_admin_files_paths = get_files_paths_list('node_models_admin.py')

    for path in node_models_admin_files_paths:
        spec = importlib.util.spec_from_file_location("node_models_admin", path)
        node_models_admin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(node_models_admin)

        node_model_admin_dict = node_models_admin.__dict__

        # Try to find the corresponding admin infos dictionary.
        try:
            preview_fields_name = node_model_name + "_preview_fields"
            preview_fields_dict = node_model_admin_dict[preview_fields_name]

        except KeyError:
            pass

        else:
            found_preview_fields_list.append((path, preview_fields_dict))

    # Allow overloaded native preview fields.
    if len(found_preview_fields_list) > 1:
        selected_preview_fields = None

        for path, found_preview_fields in found_preview_fields_list:
            if not "/bulb/" in path:
                selected_preview_fields = found_preview_fields

        return selected_preview_fields

    elif len(found_preview_fields_list) == 1:
        return found_preview_fields_list[0][1]

    return None


def get_admin_fields(node_model_name):
    """
    This function return the _fields_infos dictionary of an instance if there is one, else it return None.
    First it tries to find the related dictionary into the project. If it isn't found, it tries to find the dictionary into
    bulb natives files.

    :param node_model_name:
    :return:
    """
    found_admin_fields_list = []

    # Try to find the related admin_fields dict into the project folders and into bulb.
    node_models_admin_files_paths = get_files_paths_list('node_models_admin.py')

    for path in node_models_admin_files_paths:
        spec = importlib.util.spec_from_file_location("node_models_admin", path)
        node_models_admin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(node_models_admin)

        node_model_admin_dict = node_models_admin.__dict__

        # Try to find the corresponding admin infos dictionary.
        try:
            admin_fields_name = node_model_name + "_fields_infos"
            admin_fields_dict = node_model_admin_dict[admin_fields_name]

        except KeyError:
            pass

        else:
            found_admin_fields_list.append((path, admin_fields_dict))

    # Allow overloaded native preview fields.
    if len(found_admin_fields_list) > 1:
        selected_admin_fields = None

        for path, found_admin_fields in found_admin_fields_list:
            if not "/bulb/" in path:
                selected_admin_fields = found_admin_fields

        return selected_admin_fields

    elif len(found_admin_fields_list) == 1:
        return found_admin_fields_list[0][1]

    return None


@staff_only()
@login_required(login_page_url=login_page_url)
def handling_home_view(request):

    node_models_names = []

    # For each path of the node_models.py files :
    for node_models in get_all_node_models():
        node_models_names.append(node_models.__name__)

    return render(request, "handling/pages/handling_home.html", {"node_classes_names": node_models_names})


@staff_only()
@login_required(login_page_url=login_page_url)
def node_model_home_view(request, node_model_name):
    # Check 'view' permission.
    if request.user.has_perm("view_" + node_model_name.lower()) or request.user.has_perm("view"):

        fifteen_lasts_instances = gdbh.r_transaction("""
            MATCH (x:%s)
            RETURN x LIMIT 15
        """ % node_model_name)

        preview_fields_dict = get_admin_preview_fields(node_model_name)

        if preview_fields_dict:

            fifteen_lasts_instances_json = {}

            for instance in fifteen_lasts_instances:
                instance_properties = instance["x"]._properties
                fifteen_lasts_instances_json[instance_properties["uuid"]] = {}

                for instance_property_key, instance_property_value in instance_properties.items():
                    for admin_preview_field_key, admin_preview_field_value in preview_fields_dict.items():
                        if instance_property_key == admin_preview_field_value:

                            fifteen_lasts_instances_json[instance_properties["uuid"]][admin_preview_field_key] = (instance_property_key, instance_property_value)

                fifteen_lasts_instances_json[instance_properties["uuid"]] = dict(OrderedDict(sorted(fifteen_lasts_instances_json[instance_properties["uuid"]].items(), key=lambda t: t[0])))

            return render(request, "handling/pages/node_class_home.html", locals())

        else:
            try:
                first_instance_uuid = fifteen_lasts_instances[0]["x"]

            except IndexError:
                return redirect("node_creation", node_model_name=node_model_name)

            else:
                return redirect("node_handling", node_model_name=node_model_name, node_uuid="None")

    else:
        return redirect(settings.BULB_HOME_PAGE_URL)


@staff_only()
@login_required(login_page_url=login_page_url)
def node_handling_view(request, node_model_name, node_uuid):
    # Check 'update' permission.
    if request.user.has_perm("update_" + node_model_name.lower()) or request.user.has_perm("update"):

        # Try to get the corresponding node model
        all_node_models = get_all_node_models()
        node_model = None

        # For each path of the node_models.py files :
        for found_node_model in all_node_models:
            if found_node_model.__name__ == node_model_name:
                node_model = found_node_model

        node_uuid = str(node_uuid)

        if node_uuid == "None":
            instance = node_model.get()

        else:
            instance = node_model.get(uuid=node_uuid)

        admin_fields_dict = get_admin_fields(node_model_name)

        # Handle relationships
        all_objects_dict = {}
        selected_objects_dict = {}
        available_objects_dict = {}

        for field_name, field_settings, in admin_fields_dict.items():
            if field_settings["type"] == "relationship":
                all_objects_dict[field_name] = []

                # Get and store all the required datas for the selected_objects_dict.
                selected_objects = None

                try:
                    choices_render = field_settings['rel']['choices_render']

                except KeyError:
                    pass

                else:

                    if User in node_model.__mro__:
                        if field_name == "permissions":
                            selected_objects = eval(f"instance.{field_name}").get(order_by=choices_render[0],
                                                                                  only=["uuid"] + choices_render,
                                                                                  only_user_perms=True)
                        else:
                            selected_objects = eval(f"instance.{field_name}").get(order_by=choices_render[0],
                                                                                  only=["uuid"] + choices_render)

                    else:
                        selected_objects = eval(f"instance.{field_name}").get(order_by=choices_render[0],
                                                                              only=["uuid"] + choices_render)

                    if selected_objects is not None:
                        selected_objects_dict[field_name] = []
                        for selected_object in selected_objects:
                            values_tuple = []
                            for name, value in selected_object.items():
                                values_tuple.append(value)

                            values_tuple = tuple(values_tuple)
                            selected_objects_dict[field_name].append(values_tuple)
                            # all_objects_dict[field_name].append(values_tuple)

                    # Get and store all the required datas for the available_objects_dict.
                    for nm in all_node_models:

                        try:
                            related_node_model_name = field_settings['rel']['related_node_model_name']

                        except KeyError:
                            pass

                        else:
                            if nm.__name__ == related_node_model_name:
                                all_objects_response = {}
                                all_objects_response[field_name] = nm.get(order_by=choices_render[0],
                                                                          only=["uuid"] + choices_render)

                                if all_objects_response[field_name] is not None:
                                    for object_dict in all_objects_response[field_name]:
                                        values_tuple = []
                                        for name, value in object_dict.items():
                                            values_tuple.append(value)
                                        values_tuple = tuple(values_tuple)
                                        all_objects_dict[field_name].append(values_tuple)

                                    available_objects_dict[field_name] = []

                                    for values_tuple in all_objects_dict[field_name]:

                                        if selected_objects is not None:
                                            if values_tuple not in selected_objects_dict[field_name]:
                                                available_objects_dict[field_name].append(values_tuple)
                                        else:
                                            available_objects_dict[field_name].append(values_tuple)

        if request.POST or request.FILES:
            admin_request_post = dict(request.POST)
            admin_request_files = dict(request.FILES)
            admin_request = {**admin_request_post, **admin_request_files}

            if "action" in admin_request.keys():

                if admin_request["action"][0] == "update":

                    # Remove the action of the request and the CSRF Token before uploading the new properties
                    del admin_request["action"]
                    del admin_request["csrfmiddlewaretoken"]

                    # Store field's name and value if there is a password.
                    password_field_name = None
                    password_field_value = None
                    password_confirmation_field_name = None
                    password_confirmation_field_value = None

                    for property_name, property_value in admin_request.items():

                        if property_value[0]:
                            # Ensure that it is not an helper field.
                            try:
                                related_admin_field_dict = admin_fields_dict[property_name]

                            except KeyError:
                                pass

                            else:
                                # Handle boolean values.
                                if property_value[0] == "on":
                                    property_value[0] = True
                                elif property_value[0] == "off":
                                    property_value[0] = False

                                # Handle datetime values.
                                elif related_admin_field_dict["type"] == "datetime":
                                    if isinstance(property_value[0], str):
                                        try:
                                            property_value[0] = datetime.datetime.fromisoformat(property_value[0])

                                        # Per default the Neo4j database add timezone (represented by 9 characters) to time object.
                                        except ValueError:
                                            property_value[0] = datetime.datetime.fromisoformat(property_value[0][:-9])

                                # Handle date values.
                                elif related_admin_field_dict["type"] == "date":
                                    if isinstance(property_value[0], str):
                                        property_value[0] = datetime.date.fromisoformat(property_value[0])

                                # Handle time values.
                                elif related_admin_field_dict["type"] == "time":
                                    if isinstance(property_value[0], str):
                                        try:
                                            str_to_datetime = datetime.datetime.strptime(property_value[0], "%H:%M:%S")
                                            datetime_to_time = datetime.datetime.time(str_to_datetime)
                                            property_value[0] = datetime_to_time

                                        # Per default the Neo4j database add milisecond (represented by 10 characters) to time object.
                                        except ValueError:
                                            str_to_datetime = datetime.datetime.strptime(property_value[0][:-10], "%H:%M:%S")
                                            datetime_to_time = datetime.datetime.time(str_to_datetime)
                                            property_value[0] = datetime_to_time

                            # Helpers fields and password.

                            # Handle passwords.
                            if property_name == "password-info":
                                password_field_name = property_value[0]
                                password_confirmation_field_name = f"{property_value[0]}-confirmation"

                            elif property_name == password_field_name:
                                password_field_value = property_value

                            elif property_name == password_confirmation_field_name:
                                password_confirmation_field_value = property_value

                                if password_field_value == password_confirmation_field_value:
                                    instance.set_password(password_field_value[0])

                                else:
                                    # TODO : Ajouter l'erreur sur le formulaire
                                    add_message(
                                        request, ERROR, "Le mot de passe et sa confirmation ne correspondent pas. Le mot de passe n'a donc pas été modifié.")

                            # Handle relationships.
                            elif property_name == "relationships-helper":
                                recovered_dict = json.loads(property_value[0])

                                for field_name, field_instructions in recovered_dict.items():
                                    related_relationship_object = eval(f"instance.{field_name}")

                                    add_list = field_instructions["add"]
                                    remove_list = field_instructions["remove"]

                                    if add_list:
                                        for to_add_uuid in add_list:

                                            # Check uuid to prevent HTML modification attack.
                                            uuid_is_valid = False
                                            for other_values_tuple in all_objects_dict[field_name]:
                                                if other_values_tuple[0] == to_add_uuid:
                                                    uuid_is_valid = True
                                                    break

                                            if uuid_is_valid is False:
                                                raise BULBAdminError(
                                                    "HTML modifications was found, the modifications cannot be done.")

                                            related_relationship_object.add(uuid=to_add_uuid)

                                    if remove_list:
                                        for to_remove_uuid in remove_list:

                                            # Check uuid to prevent HTML modification attack.
                                            uuid_is_valid = False
                                            for other_values_tuple in all_objects_dict[field_name]:
                                                if other_values_tuple[0] == to_remove_uuid:
                                                    uuid_is_valid = True
                                                    break

                                            if uuid_is_valid is False:
                                                raise BULBAdminError(
                                                    "HTML modifications was found, the modifications cannot be done.")

                                            related_relationship_object.remove(uuid=to_remove_uuid)

                            # Handle unique relationships.
                            elif property_name == "unique-relationship-helper":
                                field_name = property_value[0].split(",")[0]
                                object_uuid = property_value[0].split(",")[1]

                                related_relationship_object = eval(f"instance.{field_name}")

                                # Check uuid to prevent HTML modification attack.
                                uuid_is_valid = False
                                for other_values_tuple in all_objects_dict[field_name]:
                                    if other_values_tuple[0] == object_uuid:
                                        uuid_is_valid = True
                                        break

                                if uuid_is_valid is False:
                                    raise BULBAdminError(
                                        "HTML modifications was found, the modifications cannot be done.")

                                related_relationship_object.remove(uuid=object_uuid)

                            else:
                                print("FIELDS = ", property_name, property_value[0])
                                instance.update(property_name, property_value[0])

                    add_message(request, SUCCESS, "L'instance a bien été mise à jour.")

                    if node_uuid != "None":
                        return redirect("node_model_home", node_model_name=node_model_name, permanent=True)

                    else:
                        return redirect("handling_home", permanent=True)

                if admin_request["action"][0] == "delete":
                    # Check 'delete' permission.
                    if request.user.has_perm("delete_" + node_model_name.lower()) or request.user.has_perm("delete"):

                        instance.delete()
                        add_message(request, SUCCESS, "L'instance a bien été supprimée.")

                        if node_uuid != "None":
                            return redirect("node_model_home", node_model_name=node_model_name, permanent=True)

                        else:
                            return redirect("handling_home", permanent=True)

                    else:
                        add_message(request, ERROR, "Vous n'avez pas la permission de supprimer cette instance.")
                        return redirect("node_handling", node_model_name=node_model_name, node_uuid=node_uuid)

            else:
                raise BULBAdminError("You must provide the 'action' in the POST request.")

        return render(request, "handling/pages/node_handling.html", locals())

    else:
        return redirect("node_model_home", node_model_name=node_model_name)


@staff_only()
@login_required(login_page_url=login_page_url)
def node_creation_view(request, node_model_name):
    # Check 'update' permission.
    if request.user.has_perm("create_" + node_model_name.lower()) or request.user.has_perm("create"):

        # Try to get the corresponding node model
        all_node_models = get_all_node_models()
        node_model = None

        # For each path of the node_models.py files :
        for found_node_model in all_node_models:
            if found_node_model.__name__ == node_model_name:
                node_model = found_node_model

        admin_fields_dict = get_admin_fields(node_model_name)

        # Get availables objects for relationships.
        available_objects_dict = {}

        for field_name, field_settings in admin_fields_dict.items():
            if field_settings["type"] == "relationship":

                available_objects_dict[field_name] = []

                for nm in all_node_models:
                    try:
                        related_node_model_name = field_settings['rel']['related_node_model_name']

                    except KeyError:
                        pass

                    else:
                        if nm.__name__ == field_settings['rel']['related_node_model_name']:
                            available_objects_response = {}
                            available_objects_response[field_name] = nm.get(order_by=field_settings['rel']['choices_render'][0],
                                                                            only=["uuid"] + field_settings['rel']['choices_render'])

                            if available_objects_response[field_name] is not None:
                                for object_dict in available_objects_response[field_name]:
                                    values_tuple = []
                                    for name, value in object_dict.items():
                                        values_tuple.append(value)
                                    values_tuple = tuple(values_tuple)
                                    available_objects_dict[field_name].append(values_tuple)

        if request.POST or request.FILES:
            admin_request_post = dict(request.POST)
            admin_request_files = dict(request.FILES)
            admin_request = {**admin_request_post, **admin_request_files}

            properties = {}
            relationships_dict = {}

            for key, value in admin_request.items():
                if not key == "relationships-helper":
                    properties[key] = value[0]

                else:
                    relationships_dict = json.loads(value[0])

            print("properties = ", properties)
            print("relationships = ", relationships_dict)

            del properties["csrfmiddlewaretoken"]

            try:
                password_field_name = properties["password-info"]

            except KeyError:
                pass

            else:
                password_field_value = properties[password_field_name]
                password_confirmation_field_name = f'{properties["password-info"]}-confirmation'
                password_confirmation_field_value = properties[password_confirmation_field_name]

                del properties["password-info"]
                del properties[password_confirmation_field_name]

                if not password_field_value == password_confirmation_field_value:
                    del properties[password_field_name]
                    add_message(request, ERROR, "Le mot de passe et sa confirmation ne correspondent pas. Le mot de passe n'a donc pas été défini.")


            for property_name, property_value in properties.items():
                if property_value == "on":
                    properties[property_name] = True
                if property_value == "off":
                    properties[property_name] = False

            new_instance = node_model.create(**properties)

            for rel_name, rel_instructions in relationships_dict.items():
                related_relationship_object = eval(f"new_instance.{rel_name}")

                add_list = rel_instructions["add"]

                if add_list:
                    for to_add_uuid in add_list:

                        # Check uuid to prevent HTML modification attack.
                        uuid_is_valid = False
                        for other_values_tuple in available_objects_dict[rel_name]:
                            if other_values_tuple[0] == to_add_uuid:
                                uuid_is_valid = True
                                break

                        if uuid_is_valid is False:
                            raise BULBAdminError(
                                "HTML modifications was found, the modifications cannot be done.")

                        related_relationship_object.add(uuid=to_add_uuid)

            add_message(request, SUCCESS, "L'instance a bien été créée.")

            admin_preview_fields = get_admin_preview_fields(node_model_name)
            if admin_preview_fields is not False:
                return redirect("node_model_home", node_model_name=node_model_name, permanent=True)

            else:
                return redirect("handling_home", permanent=True)

        return render(request, "handling/pages/node_creation.html", locals())

    else:
        return redirect("node_model_home", node_model_name=node_model_name)
