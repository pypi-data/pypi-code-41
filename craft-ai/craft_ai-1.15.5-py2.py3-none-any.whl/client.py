# To avoid conflicts between python's own 'time' and this 'time.py'
# cf. https://stackoverflow.com/a/28854227
from __future__ import absolute_import

import json
import time
import datetime

from platform import python_implementation, python_version

import requests
import six
import pandas as pd

from craftai import __version__ as pkg_version
from craftai.constants import AGENT_ID_PATTERN, DEFAULT_DECISION_TREE_VERSION
from craftai.errors import CraftAiCredentialsError, CraftAiBadRequestError, CraftAiNotFoundError
from craftai.errors import CraftAiUnknownError, CraftAiInternalError, CraftAiLongRequestTimeOutError
from craftai.errors import CraftAiNetworkError
from craftai.interpreter import Interpreter
from craftai.jwt_decode import jwt_decode

USER_AGENT = "craft-ai-client-python/{} [{} {}]".format(pkg_version,
                                                        python_implementation(),
                                                        python_version())

ERROR_ID_MESSAGE = ("Invalid agent id given.\n"
                    "It must be a string containing only\n"
                    "characters in \"a-zA-Z0-9_-\" \n"
                    "and must be between 1 and 36 characters.")

def current_time_ms():
  return int(round(time.time() * 1000))

class CraftAIClient(object):
  """Client class for craft ai's API"""

  def __init__(self, cfg):
    self._base_url = ""
    self._headers = {}
    self._config = {}
    # Requests session: connection pooling and base configuration for all requests
    self._requests_session = requests.Session()

    try:
      self.config = cfg
    except (CraftAiCredentialsError, CraftAiBadRequestError) as err:
      raise err

  @property
  def config(self):
    return self._config

  @config.setter
  def config(self, cfg):
    cfg = cfg.copy()
    (payload, _, _, _) = jwt_decode(cfg.get("token"))
    cfg["owner"] = cfg["owner"] if "owner" in cfg else payload.get("owner")
    cfg["project"] = cfg["project"] if "project" in cfg else payload.get("project")
    cfg["url"] = cfg["url"] if "url" in cfg else payload.get("platform")

    if not isinstance(cfg.get("project"), six.string_types):
      raise CraftAiCredentialsError("""Unable to create client with no"""
                                    """ or invalid project provided.""")
    else:
      splitted_project = cfg.get("project").split("/")
      if len(splitted_project) == 2:
        cfg["owner"] = splitted_project[0]
        cfg["project"] = splitted_project[1]
      elif len(splitted_project) > 2:
        raise CraftAiCredentialsError("""Unable to create client with invalid"""
                                      """ project name.""")
    if not isinstance(cfg.get("owner"), six.string_types):
      raise CraftAiCredentialsError("""Unable to create client with no"""
                                    """ or invalid owner provided.""")
    if not isinstance(cfg.get("operationsChunksSize"), six.integer_types):
      cfg["operationsChunksSize"] = 200
    if (cfg.get("decisionTreeRetrievalTimeout") is not False and
        not isinstance(cfg.get("decisionTreeRetrievalTimeout"), six.integer_types)):
      cfg["decisionTreeRetrievalTimeout"] = 1000 * 60 * 5 # 5 minutes
    if not isinstance(cfg.get("url"), six.string_types):
      cfg["url"] = "https://beta.craft.ai"
    if cfg.get("url").endswith("/"):
      raise CraftAiBadRequestError("""Unable to create client with"""
                                   """ invalid url provided. The url"""
                                   """ should not terminate with a"""
                                   """ slash.""")
    self._config = cfg

    self._base_url = "{}/api/v1/{}/{}".format(self.config["url"],
                                              self.config["owner"],
                                              self.config["project"])

    if cfg.get("proxy"):
      scheme = six.moves.urllib.parse.urlparse(self.config["url"]).scheme
      if not scheme:
        raise CraftAiCredentialsError("""Unable to create client with an URL"""
                                      """ without a scheme. Cannot configure"""
                                      """ the proxy.""")
      proxies = {}
      proxies[scheme] = cfg.get("proxy")
      self._requests_session.proxies = proxies
    # Headers have to be set here to avoid multiple definitions
    # of the 'Authorization' header if config is modified
    base_headers = {}
    base_headers["Authorization"] = "Bearer " + self.config.get("token")
    base_headers["User-Agent"] = USER_AGENT
    self._requests_session.headers = base_headers

  #################
  # Agent methods #
  #################

  def create_agent(self, configuration, agent_id=""):
    """Create an agent.

    :param dict configuration: Form given by the craftai documentation.
    :param str agent_id: Optional. The id of the agent to create. It
    must be an str containing only characters in "a-zA-Z0-9_-" and
    must be between 1 and 36 characters.
    :default agent_id: "", the agent_id is generated.

    :return: agent created.
    :rtype: dict.

    :raise CraftAiBadRequestError: if the input is not of
    the right form.
    """
    # Extra header in addition to the main session's
    ct_header = {"Content-Type": "application/json; charset=utf-8"}

    # Building payload and checking that it is valid for a JSON
    # serialization
    payload = {"configuration": configuration}

    if agent_id != "":
      # Raises an error when agent_id is invalid
      self._check_agent_id(agent_id)

      payload["id"] = agent_id

    try:
      json_pl = json.dumps(payload)
    except TypeError as err:
      raise CraftAiBadRequestError("Invalid configuration or agent id given. {}"
                                   .format(err.__str__()))

    req_url = "{}/agents".format(self._base_url)
    resp = self._requests_session.post(req_url, headers=ct_header, data=json_pl)

    agent = self._decode_response(resp)

    return agent

  def create_agents_bulk(self, payload):
    """Create a group of agents.

    :param list payload: Contains the informations to create the agents.
    It's in the form [{"id": agent_id, "configuration": configuration}]
    With an optional id key that is an str containing only characters
    in "a-zA-Z0-9_-" and must be between 1 and 36 characters.
    With configuration having the form given in the craftai documentation.

    :return: agents created which are represented with dictionnaries.
    :rtype: List of dict.

    :raises CraftAiBadRequestError: If all of the ids or all of the
    configurations are invalid.
    """
    # Check all ids, raise an error if all ids are invalid
    valid_indices, invalid_indices, invalid_agents = self._check_agent_id_bulk(payload)

    # Create the json file with the agents with valid id and send it
    valid_agents = self._create_and_send_json_bulk([payload[i] for i in valid_indices],
                                                   "{}/bulk/agents".format(self._base_url),
                                                   "POST")

    if invalid_indices == []:
      return valid_agents

    # Put the valid and invalid agents in their original index
    return self._recreate_list_with_indices(valid_indices,
                                            valid_agents,
                                            invalid_indices,
                                            invalid_agents)

  def get_agent(self, agent_id):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    req_url = "{}/agents/{}".format(self._base_url, agent_id)
    resp = self._requests_session.get(req_url)

    agent = self._decode_response(resp)

    return agent

  def list_agents(self):

    req_url = "{}/agents".format(self._base_url)
    resp = self._requests_session.get(req_url)

    agents = self._decode_response(resp)

    return agents["agentsList"]

  def delete_agent(self, agent_id):
    """Delete an agent.

    :param str agent_id: The id of the agent to delete. It must
    be an str containing only characters in "a-zA-Z0-9_-" and
    must be between 1 and 36 characters.

    :return: agent deleted.
    :rtype: dict.
    """
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    req_url = "{}/agents/{}".format(self._base_url, agent_id)
    resp = self._requests_session.delete(req_url)

    decoded_resp = self._decode_response(resp)

    return decoded_resp

  def delete_agents_bulk(self, payload):
    """Delete a group of agents

    :param list payload: Contains the informations to delete the agents.
    It's in the form [{"id": agent_id}].
    With id an str containing only characters in "a-zA-Z0-9_-" and must
    be between 1 and 36 characters.

    :return: the list of agents deleted which are represented with
    dictionnaries.
    :rtype: list of dict.

    :raises CraftAiBadRequestError: If all of the ids are invalid.
    """
    # Check all ids, raise an error if all ids are invalid
    valid_indices, invalid_indices, invalid_agents = self._check_agent_id_bulk(payload)

    # Create the json file with the agents with valid id and send it
    valid_agents = self._create_and_send_json_bulk([payload[i] for i in valid_indices],
                                                   "{}/bulk/agents".format(self._base_url),
                                                   "DELETE")

    if invalid_indices == []:
      return valid_agents

    # Put the valid and invalid agents in their original index
    return self._recreate_list_with_indices(valid_indices,
                                            valid_agents,
                                            invalid_indices,
                                            invalid_agents)

  def get_shared_agent_inspector_url(self, agent_id, timestamp=None):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    req_url = "{}/agents/{}/shared".format(self._base_url, agent_id)
    resp = self._requests_session.get(req_url)

    url = self._decode_response(resp)

    if timestamp is not None:
      return "{}?t={}".format(url["shortUrl"], str(timestamp))

    return url["shortUrl"]

  def delete_shared_agent_inspector_url(self, agent_id):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    req_url = "{}/agents/{}/shared".format(self._base_url, agent_id)
    resp = self._requests_session.delete(req_url)

    decoded_resp = self._decode_response(resp)

    return decoded_resp

  ###################
  # Context methods #
  ###################

  def add_operations(self, agent_id, operations):
    """Add operations to an agent.

    :param str agent_id: The id of the agent to delete. It must be
    an str containing only characters in "a-zA-Z0-9_-" and must be
    between 1 and 36 characters. It must referenced an existing agent.
    :param list operations: Contains dictionnaries that has the
    form given in the craftai documentation and the configuration
    of the agent.

    :return: message about the added operations.
    :rtype: str

    :raise CraftAiBadRequestError: if the input is not of
    the right form.
    """
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    # Extra header in addition to the main session's
    ct_header = {"Content-Type": "application/json; charset=utf-8"}
    offset = 0

    is_looping = True

    while is_looping:
      next_offset = offset + self.config["operationsChunksSize"]

      try:
        json_pl = json.dumps(operations[offset:next_offset])
      except TypeError as err:
        raise CraftAiBadRequestError("Invalid configuration or agent id given. {}"
                                     .format(err.__str__()))

      req_url = "{}/agents/{}/context".format(self._base_url, agent_id)
      resp = self._requests_session.post(req_url, headers=ct_header, data=json_pl)
      self._decode_response(resp)

      if next_offset >= len(operations):
        is_looping = False

      offset = next_offset

    return {
      "message": "Successfully added %i operation(s) to the agent \"%s/%s/%s\" context."
                 % (len(operations), self.config["owner"], self.config["project"], agent_id)
    }

  def _add_operations_bulk(self, chunked_data):
    """Tool for the function add_operations_bulk. It send the requests to
    add the operations to the agents.

    :param list chunked_data: list of list of the agents and their operations
    to add. Each chunk can be requested at the same time.

    :return: list of agents containing a message about the added
    operations.
    :rtype: list of dict.

    :raises CraftAiBadRequestError: if the input is not of the right form.
    """
    url = "{}/bulk/context".format(self._base_url)
    ct_header = {"Content-Type": "application/json; charset=utf-8"}

    responses = []
    for chunk in chunked_data:
      if len(chunk) > 1:
        try:
          json_pl = json.dumps(chunk)
        except TypeError as err:
          raise CraftAiBadRequestError("Error while dumping the payload into json"
                                       "format when converting it for the bulk request. {}"
                                       .format(err.__str__()))
        resp = self._requests_session.post(url, headers=ct_header, data=json_pl)
        resp = self._decode_response(resp)
        responses += resp
      elif chunk:
        message = self.add_operations(chunk[0]["id"], chunk[0]["operations"])
        responses.append({"id": chunk[0]["id"], "status": 201, "message": message})

    if responses == []:
      raise CraftAiBadRequestError("Invalid or empty set of operations given")

    return responses

  def add_operations_bulk(self, payload):
    """Add operations to a group of agents.

    :param list payload: contains the informations necessary for the action.
    It's in the form [{"id": agent_id, "operations": operations}]
    With id that is an str containing only characters in "a-zA-Z0-9_-"
    and must be between 1 and 36 characters. It must referenced an
    existing agent.
    With operations a list containing dictionnaries that has the form given
    in the craftai documentation and the configuration of the agent.

    :return: list of agents containing a message about the added
    operations.
    :rtype: list of dict.

    :raises CraftAiBadRequestError: if all of the ids are invalid or
    referenced non existing agents or one of the operations is invalid.
    """
    # Check all ids, raise an error if all ids are invalid
    valid_indices, _, _ = self._check_agent_id_bulk(payload)
    valid_payload = [payload[i] for i in valid_indices]

    chunked_data = []
    current_chunk = []
    current_chunk_size = 0

    for agent in valid_payload:
      if (agent["operations"] and isinstance(agent["operations"], list)):
        if current_chunk_size + len(agent["operations"]) > self.config["operationsChunksSize"]:
          chunked_data.append(current_chunk)
          current_chunk_size = 0
          current_chunk = []
        if len(agent["operations"]) > self.config["operationsChunksSize"]:
          chunked_data.append([agent])
          current_chunk_size = 0
        else:
          current_chunk_size += len(agent["operations"])
          current_chunk.append(agent)

    if current_chunk:
      chunked_data.append(current_chunk)

    return self._add_operations_bulk(chunked_data)

  def _get_operations_list_pages(self, url, ops_list):
    if url is None:
      return ops_list

    resp = self._requests_session.get(url)

    new_ops_list = self._decode_response(resp)
    next_page_url = resp.headers.get("x-craft-ai-next-page-url")

    return self._get_operations_list_pages(next_page_url, ops_list + new_ops_list)

  def get_operations_list(self, agent_id, start=None, end=None):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    req_url = "{}/agents/{}/context".format(self._base_url, agent_id)
    req_params = {
      "start": start,
      "end": end
    }
    resp = self._requests_session.get(req_url, params=req_params)

    initial_ops_list = self._decode_response(resp)
    next_page_url = resp.headers.get("x-craft-ai-next-page-url")

    return self._get_operations_list_pages(next_page_url, initial_ops_list)

  def _get_state_history_pages(self, url, state_history):
    if url is None:
      return state_history

    resp = self._requests_session.get(url)

    new_state_history = self._decode_response(resp)
    next_page_url = resp.headers.get("x-craft-ai-next-page-url")

    return self._get_state_history_pages(next_page_url, state_history + new_state_history)

  def get_state_history(self, agent_id, start=None, end=None):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    req_url = "{}/agents/{}/context/state/history".format(self._base_url, agent_id)
    req_params = {
      "start": start,
      "end": end
    }
    resp = self._requests_session.get(req_url, params=req_params)

    initial_states_history = self._decode_response(resp)
    next_page_url = resp.headers.get("x-craft-ai-next-page-url")

    return self._get_state_history_pages(next_page_url, initial_states_history)

  def get_context_state(self, agent_id, timestamp):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    req_url = "{}/agents/{}/context/state?t={}".format(self._base_url,
                                                       agent_id,
                                                       timestamp)
    resp = self._requests_session.get(req_url)

    context_state = self._decode_response(resp)

    return context_state

  #########################
  # Decision tree methods #
  #########################

  def _get_decision_tree(self, agent_id, timestamp, version=DEFAULT_DECISION_TREE_VERSION):
    """Tool for the function get_decision_tree.

    :param str agent_id: the id of the agent to get the tree. It
    must be an str containing only characters in "a-zA-Z0-9_-" and
    must be between 1 and 36 characters.
    :param int timestamp: Optional. The decision tree is comptuted
    at this timestamp.
    :default timestamp: None, means that we get the tree computed
    with all its context history.
    :param version: version of the tree to get.
    :type version: str or int.
    :default version: default version of the tree.

    :return: decision tree.
    :rtype: dict.
    """
    self._requests_session.headers["x-craft-ai-tree-version"] = version

    # If we give no timestamp the default behaviour is to give the tree from the latest timestamp
    if timestamp is None:
      req_url = "{}/agents/{}/decision/tree?".format(self._base_url, agent_id)
    else:
      req_url = "{}/agents/{}/decision/tree?t={}".format(self._base_url, agent_id, timestamp)

    resp = self._requests_session.get(req_url)

    decision_tree = self._decode_response(resp)

    return decision_tree

  def get_decision_tree(self, agent_id, timestamp=None, version=DEFAULT_DECISION_TREE_VERSION):
    """Get decision tree.

    :param str agent_id: the id of the agent to get the tree. It
    must be an str containing only characters in "a-zA-Z0-9_-" and
    must be between 1 and 36 characters.
    :param int timestamp: Optional. The decision tree is comptuted
    at this timestamp.
    :default timestamp: None, means that we get the tree computed
    with all its context history.
    :param version: version of the tree to get.
    :type version: str or int.
    :default version: default version of the tree.

    :return: decision tree.
    :rtype: dict.

    :raises CraftAiLongRequestTimeOutError: if the API doesn't get
    the tree in the time given by the configuration.
    """
    if isinstance(version, int):
      version = str(version)

    # Convert datetime to timestamp
    if isinstance(timestamp, pd.Timestamp):
      timestamp = timestamp.value // 10 ** 9
    elif isinstance(timestamp, datetime.datetime):
      timestamp = time.mktime(timestamp.timetuple())

    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)
    if self._config["decisionTreeRetrievalTimeout"] is False:
      # Don't retry
      return self._get_decision_tree(agent_id, timestamp, version)

    start = current_time_ms()
    while True:
      now = current_time_ms()
      if now - start > self._config["decisionTreeRetrievalTimeout"]:
        # Client side timeout
        raise CraftAiLongRequestTimeOutError()
      try:
        return self._get_decision_tree(agent_id, timestamp, version)
      except CraftAiLongRequestTimeOutError:
        # Do nothing and continue.
        continue

  def _get_decision_trees_bulk(self, payload, valid_indices, invalid_indices, invalid_dts):
    """Tool for the function get_decision_trees_bulk.

    :param list payload: contains the informations necessary for getting
    the trees. Its form is the same than for the function.
    get_decision_trees_bulk.
    :param list valid_indices: list of the indices of the valid agent id.
    :param list invalid_indices: list of the indices of the valid agent id.
    :param list invalid_dts: list of the invalid agent id.

    :return: decision trees.
    :rtype: list of dict.
    """
    valid_dts = self._create_and_send_json_bulk([payload[i] for i in valid_indices],
                                                "{}/bulk/decision_tree".format(self._base_url),
                                                "POST")

    if invalid_indices == []:
      return valid_dts

    # Put the valid and invalid decision trees in their original index
    return self._recreate_list_with_indices(valid_indices, valid_dts, invalid_indices, invalid_dts)

  def get_decision_trees_bulk(self, payload, version=DEFAULT_DECISION_TREE_VERSION):
    """Get a group of decision trees.

    :param list payload: contains the informations necessary for getting
    the trees. It's in the form [{"id": agent_id, "timestamp": timestamp}]
    With id a str containing only characters in "a-zA-Z0-9_-" and must be
    between 1 and 36 characters. It must referenced an existing agent.
    With timestamp an positive and not null integer.
    :param version: version of the tree to get.
    :type version: str or int.
    :default version: default version of the tree.

    :return: Decision trees.
    :rtype: list of dict.

    :raises CraftAiBadRequestError: if all of the ids are invalid or
    referenced non existing agents or all of the timestamp are invalid.
    :raises CraftAiLongRequestTimeOutError: if the API doesn't get
    the tree in the time given by the configuration.
    """
    if isinstance(version, int):
      version = str(version)
    self._requests_session.headers["x-craft-ai-tree-version"] = version

    # Check all ids, raise an error if all ids are invalid
    valid_indices, invalid_indices, invalid_dts = self._check_agent_id_bulk(payload)

    if self._config["decisionTreeRetrievalTimeout"] is False:
      # Don't retry
      return self._get_decision_trees_bulk(payload,
                                           valid_indices,
                                           invalid_indices,
                                           invalid_dts)
    start = current_time_ms()
    while True:
      now = current_time_ms()
      if now - start > self._config["decisionTreeRetrievalTimeout"]:
        # Client side timeout
        raise CraftAiLongRequestTimeOutError()
      try:
        return self._get_decision_trees_bulk(payload,
                                             valid_indices,
                                             invalid_indices,
                                             invalid_dts)
      except CraftAiLongRequestTimeOutError:
        # Do nothing and continue.
        continue

  @staticmethod
  def decide(tree, *args):
    return Interpreter.decide(tree, args)

  @staticmethod
  def _parse_body(response):
    try:
      return response.json()
    except:
      raise CraftAiInternalError(
        "Internal Error, the craft ai server responded in an invalid format."
      )

  @staticmethod
  def _decode_response(response):
    """Decode the response of a request.

    :param response: response of a request.

    :return: decoded response.

    :raise Error: Raise the error given by the request.
    """
    status_code = response.status_code

    message = "Status code " + str(status_code)
    try:
      message = CraftAIClient._parse_body(response)["message"]
    except (CraftAiInternalError, KeyError, TypeError):
      pass

    if status_code in [200, 201, 204, 207]:
      return CraftAIClient._parse_body(response)
    else:
      raise CraftAIClient._get_error_from_status(status_code, message)
    return None

  @staticmethod
  def _decode_response_bulk(response_bulk):
    """Decode the response of each agent given by a bulk function.

    :param list response_bulk: list of dictionnary which represents
    the response for an agent.

    :return: decoded response.
    :rtype: list of dict.
    """
    resp = []
    for response in response_bulk:
      if ("status" in response) and (response.get("status") == 201):
        agent = {"id": response["id"],
                 "message": response["message"]}
        resp.append(agent)
      elif "status" in response:
        status_code = response["status"]
        message = response["message"]
        agent = {"error": CraftAIClient._get_error_from_status(status_code, message)}
        try:
          agent["id"] = response["id"]
        except KeyError:
          pass
        resp.append(agent)

      else:
        resp.append(response)

    return resp

  @staticmethod
  def _get_error_from_status(status_code, message):
    """Give the error corresponding to the status code.

    :param int status_code: status code of the response to
    a request.
    :param str message: error message given by the response.

    :return: error corresponding to the status code.
    :rtype: Error.
    """
    if status_code == 202:
      err = CraftAiLongRequestTimeOutError(message)
    elif status_code == 401 or status_code == 403:
      err = CraftAiCredentialsError(message)
    elif status_code == 400:
      err = CraftAiBadRequestError(message)
    elif status_code == 404:
      err = CraftAiNotFoundError(message)
    elif status_code == 413:
      err = CraftAiBadRequestError("Given payload is too large")
    elif status_code == 500:
      err = CraftAiInternalError(message)
    elif status_code == 503:
      err = CraftAiNetworkError("""Service momentarily unavailable, please try"""
                                """again in a few minutes. If the problem """
                                """persists please contact us at support@craft.ai""")
    elif status_code == 504:
      err = CraftAiBadRequestError("Request has timed out")
    else:
      err = CraftAiUnknownError(message)

    return err

  @staticmethod
  def _check_agent_id(agent_id):
    """Checks that the given agent_id is a valid non-empty string.

    :param str agent_id: agent id to check.

    :raise CraftAiBadRequestError: If the given agent_id is not of
    type string or if it is an empty string.
    """
    if (not isinstance(agent_id, six.string_types) or
        AGENT_ID_PATTERN.match(agent_id) is None):
      raise CraftAiBadRequestError(ERROR_ID_MESSAGE)

  def _check_agent_id_bulk(self, payload, check_serializable=True):
    """Checks that all the given agent ids are valid non-empty strings
    and if the agents are serializable.

    :param list payload: list of dictionnary which represents an agent.

    :return: list of the agents with valid ids, list of the agents with
    invalid ids, list of the dictionnaries with valid ids.
    :rtype: list, list, list of dict.

    :raise CraftAiBadRequestError: If all the agents are invalid.
    """
    invalid_agent_indices = []
    valid_agent_indices = []
    invalid_payload = []
    for index, agent in enumerate(payload):
      # Check if the agent ID is valid
      try:
        if "id" in agent:
          self._check_agent_id(agent["id"])
      except CraftAiBadRequestError:
        invalid_agent_indices.append(index)
        invalid_payload.append({"id": agent["id"],
                                "error": CraftAiBadRequestError(ERROR_ID_MESSAGE)})
      else:
        if check_serializable:
          # Check if the agent is serializable
          try:
            json.dumps([agent])
          except TypeError as err:
            invalid_agent_indices.append(index)
            invalid_payload.append({"id": agent["id"],
                                    "error": err})
          else:
            valid_agent_indices.append(index)
        else:
          valid_agent_indices.append(index)

    if len(invalid_agent_indices) == len(payload):
      raise CraftAiBadRequestError(ERROR_ID_MESSAGE)

    return valid_agent_indices, invalid_agent_indices, invalid_payload

  @staticmethod
  def _recreate_list_with_indices(indices1, values1, indices2, values2):
    """Create a list in the right order.

    :param list indices1: contains the list of indices corresponding to
    the values in values1.
    :param list values1: contains the first list of values.
    :param list indices2: contains the list of indices corresponding to
    the values in values2.
    :param list values2: contains the second list of values.

    :return: list of the values in the correct order.
    :rtype: list.
    """
    # Test if indices are continuous
    list_indices = sorted(indices1 + indices2)
    for i, index in enumerate(list_indices):
      if i != index:
        raise CraftAiInternalError("The agents's indices are not continuous")

    full_list = [None] * (len(indices1) + len(indices2))
    for i, index in enumerate(indices1):
      full_list[index] = values1[i]
    for i, index in enumerate(indices2):
      full_list[index] = values2[i]
    return full_list

  def _create_and_send_json_bulk(self, payload, req_url, request_type="POST"):
    """Create a json, do a request to the URL and process the response.

    :param list payload: contains the informations necessary for the action.
    It's a list of dictionnary.
    :param str req_url: URL to request with the payload.
    :param str request_type: type of request, either "POST" or "DELETE".
    :default request_type: "POST".

    :return: response of the request.
    :rtype: list of dict.

    :raises CraftAiBadRequestError: if the payload doesn't have the
    correct form to be transformed into a json or request_type is
    neither "POST" or "DELETE".
    """
    # Extra header in addition to the main session's
    ct_header = {"Content-Type": "application/json; charset=utf-8"}

    try:
      json_pl = json.dumps(payload)
    except TypeError as err:
      raise CraftAiBadRequestError("Error while dumping the payload into json"
                                   "format when converting it for the bulk request. {}"
                                   .format(err.__str__()))

    if request_type == "POST":
      resp = self._requests_session.post(req_url, headers=ct_header, data=json_pl)
    elif request_type == "DELETE":
      resp = self._requests_session.delete(req_url, headers=ct_header, data=json_pl)
    else:
      raise CraftAiBadRequestError("Request for the bulk API should be either a POST or DELETE"
                                   "request")

    agents = self._decode_response(resp)
    agents = self._decode_response_bulk(agents)

    return agents
