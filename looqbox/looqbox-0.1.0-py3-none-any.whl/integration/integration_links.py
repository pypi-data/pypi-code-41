import logging
import sys
import datetime
import json
import requests
from looqbox.view.response_board import ResponseBoard
from looqbox.view.response_board import ResponseFrame
from looqbox.objects.looq_message import ObjMessage
from looqbox.view.view_functions import frame_to_board
from looqbox.view.view_functions import response_to_frame
from looqbox.global_calling import GlobalCalling
from looqbox.integration.looqbox_global import Looqbox

__all__ = ["look_tag", "looq_test_question", "view", "get_sso_attributes", "user_id", "user_group_id", "user_login", "question_link"]

# Calling global variable
if GlobalCalling.looq.home is not None:
    GlobalCalling.set_looq_attributes(Looqbox())


def get_parser_api_version():
    """
    This function is called by the JAVA to identify the parser's version.

    :return: Parser version
    """
    parser_version = 2

    return parser_version


def _send_to_dev_link(url, response_board: ResponseBoard, show_json=False):
    """
    Function to test the return from scripts in Looqbox's interface

    :param url: Looqbox's client url
    :param response_board: Board resulting from the script
    :param show_json: Print JSON or not
    :return: A request from an api
    """
    response_json = response_board.to_json_structure

    if show_json is True:
        print(response_json)

    try:
        link_request = requests.post(url, data=response_json)
    except requests.ConnectionError:
        logging.error("Page not found -> {0}".format(url))
        sys.exit(1)

    return link_request


def _new_look_tag(tag, par_json, default, only_value):
    """
    Function to return the look tag using the new JSON format (Version 2)

    """
    if isinstance(tag, list):
        if any(tag_value for tag_value in tag if tag_value in par_json.keys()):
            if only_value:
                tags_list = [content['value'][0] for tag_value in tag for content in par_json[tag_value]['content']]
            else:
                tags_list = [content for tag_value in tag for content in par_json[tag_value]['content']]
            return tags_list
    elif tag in par_json.keys():
        if only_value:
            tags_list = list()
            for content in par_json[tag]['content']:
                tags_list.append(content['value'])

            # Flatten the lists in only one
            tags_list = [value for value_list in tags_list for value in value_list]

            return tags_list
        else:
            return par_json[tag]['content'][0]
    else:
        return default


def _old_look_tag(tag, par_json, default):
    if isinstance(tag, list):
        tags_list = [content for tag_value in tag for content in par_json[tag_value]]
        return tags_list
    elif tag in par_json.keys():
        return par_json[tag]
    else:
        return default


def look_tag(tag, par_json, default=None, only_value=True):
    """
    Function to search for a specific tag inside the JSON sent by the parser

    :param tag: Name to be found
    :param par_json: JSON from parser
    :param default: Default value to be returned
    :param only_value: If True return only the value of the tag, if the value is False the function will return all
    the JSON structure link to this tag
    :return: A JSON structure or a single value
    """

    if "apiVersion" not in par_json.keys():
        tag_value = _old_look_tag(tag, par_json, default)
    elif par_json["apiVersion"] is None:
        tag_value = _old_look_tag(tag, par_json, default)
    elif par_json["apiVersion"] == 1:
        tag_value = _old_look_tag(tag, par_json, default)
    elif par_json["apiVersion"] == 2:
        tag_value = _new_look_tag(tag, par_json, default, only_value)

    return tag_value


def _response_json(parser_json, function_call):
    """
    Function called by the python kernel inside the looqbox server. This function get the return in the main script
    and treat it to return a board to the frontend

    :param parser_json: JSON from parser
    :param function_call: Main function to be called inside the kernel. Default: looq_response
    :return: A ResponseBoard object
    """
    par = json.loads(parser_json)
    # how to get looq.response globally, put inside the class looqbox?
    response = function_call(par)
    is_board = isinstance(response, ResponseBoard)
    is_frame = isinstance(response, ResponseFrame)
    is_list = isinstance(response, list)

    if not is_frame and not is_board and is_list:
        response = frame_to_board(response)
    elif not is_frame and not is_board:
        looq_object = response_to_frame(response)
        response = frame_to_board(looq_object)
    elif is_frame:
        response = frame_to_board(response)

    board_json = response.to_json_structure
    # test when possible
    return board_json


def _check_test_parameter(parameters, par_name):
    """
    Function to check if the parameter_name(par_name) is on the parameter's keys

    :param parameters: Parameters send in looq_test_question
    :param par_name: Desire name to be found in key
    :return: The value of the par_name in parameter or None
    """
    par_return = None

    if hasattr(parameters, par_name):
        par_return = parameters[par_name]

    return par_return


def looq_test_question(test_function=None, parameters=None, show_json=False, user=None, host=None):
    """
    Function to simulate parser parameters. Using this developers can test their scripts using entities.

    :param parameters: Entities and its values
    :param show_json: Show final json or not
    :param user: User that the result will be sent
    :param host: Host that the result will be sent
    """
    # test when the process of response is correct
    if test_function is None:
        raise Exception("Function to be tested not been informed")

    if user is None:
        user = GlobalCalling.looq.user.login

    if host is None:
        host = GlobalCalling.looq.client_host

    if GlobalCalling.looq.test_mode is False:
        return None

    GlobalCalling.looq.user_id = _check_test_parameter(parameters, "user_id")
    GlobalCalling.looq.user_group_id = _check_test_parameter(parameters, "user_group_id")
    GlobalCalling.looq.user_login = _check_test_parameter(parameters, "user_login")

    initial_response_time = datetime.datetime.now()
    response = test_function(parameters)
    total_response_time = datetime.datetime.now() - initial_response_time

    if GlobalCalling.looq.publish_test is None or GlobalCalling.looq.publish_test is True:
        start_post_time = datetime.datetime.now()
        view(response, show_json, user, host)
        total_publish_time = datetime.datetime.now() - start_post_time
        print("Response time: " + str(total_response_time))
        print("Publish time: " + str(total_publish_time))
        print("Total time...:" + str(total_publish_time + total_response_time))


def view(looq_object=None, show_json=False, user=GlobalCalling.looq.user.login,
              host=GlobalCalling.looq.client_host):
    if looq_object is None:
        actual_datetime = datetime.datetime.now()

        if looq_object is None:
            looq_object = ObjMessage(text="teste " + str(actual_datetime), type="alert-success")

    is_board = isinstance(looq_object, ResponseBoard)
    is_frame = isinstance(looq_object, ResponseFrame)
    is_list = isinstance(looq_object, list)

    if not is_frame and not is_board and is_list:
        looq_object = frame_to_board(looq_object)
    elif not is_frame and not is_board:
        looq_object = response_to_frame(looq_object)
        looq_object = frame_to_board(looq_object)
    elif is_frame:
        looq_object = frame_to_board(looq_object)

    url = host + "/api/devlink/" + user
    _send_to_dev_link(url, looq_object, show_json)
    print("looq.view: published for user", user, "in", host)


def looq_process_form_json(form_json, session_json, looq_process_form):
    """
    Function that will receive a form sent by the front. This function will read the parameters and execute then
    inside the looq_process_form in the other script.
    """

    form_data = json.loads(form_json)

    session_data = json.loads(session_json)

    response = looq_process_form(form_data , session_data )

    response = json.dumps(response.to_json_structure)

    return response


def get_sso_attributes(par):
    """
    Get the user SSO information from parser

    :return: The JSON of userSsoAttributes in parser return
    """

    if "userSsoAttributes" not in par.keys():
        return []
    else:
        return par["userSsoAttributes"]


def question_link(question, link_text):
    """
    Creates a link to a question.

    :param str question: Question.
    :param str link_text: Text of the link.
    :return: A link string.
    """
    return "<question-link query='" + question + "'>" + link_text + "</question-link>"


def user_id():
    """
    Get the user id from options

    Examples:
    --------
    >>> user_id()

    :return: The id string.
    """
    return GlobalCalling.looq.user.id


def user_login():
    """
    Get the user login from options

    Examples:
    --------
    >>> user_login()

    :return: The login string.
    """
    return GlobalCalling.looq.user.login


def user_group_id():
    """
    Get the user group id from options

    Examples:
    --------
    >>> user_group_id()

    :return: The group id string.
    """
    return GlobalCalling.looq.user.group

