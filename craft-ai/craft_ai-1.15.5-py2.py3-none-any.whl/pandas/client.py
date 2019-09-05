import json
import pandas as pd
from six.moves import range

from .. import Client as VanillaClient
from ..errors import CraftAiBadRequestError
from .interpreter import Interpreter
from .utils import format_input, is_valid_property_value, create_timezone_df

def chunker(to_be_chunked_df, chunk_size):
  return (to_be_chunked_df[pos:pos + chunk_size]
          for pos in range(0, len(to_be_chunked_df), chunk_size))

class Client(VanillaClient):
  """Client class for craft ai's API using pandas dataframe types"""

  def add_operations(self, agent_id, operations):
    if isinstance(operations, pd.DataFrame):
      if not isinstance(operations.index, pd.DatetimeIndex):
        raise CraftAiBadRequestError("Invalid dataframe given, it is not time indexed.")
      if operations.index.tz is None:
        raise CraftAiBadRequestError("""tz-naive DatetimeIndex are not supported,
                                     it must be tz-aware.""")
      agent = super(Client, self).get_agent(agent_id)
      operations = operations.copy(deep=True)

      tz_col = [key for key, value in agent["configuration"]["context"].items()
                if value["type"] == "timezone"]
      if tz_col:
        tz_col = tz_col[0]
        operations[tz_col] = create_timezone_df(operations, tz_col).iloc[:, 0]

      chunk_size = self.config["operationsChunksSize"]
      for chunk in chunker(operations, chunk_size):
        chunk_operations = [
          {
            "timestamp": row.name.value // 10 ** 9, # Timestamp.value returns nanoseconds
            "context": {
              col: format_input(row[col])
              for col in chunk.columns if is_valid_property_value(col, row[col])
            }
          } for _, row in chunk.iterrows()
        ]
        super(Client, self).add_operations(agent_id, chunk_operations)

      return {
        "message": "Successfully added %i operation(s) to the agent \"%s/%s/%s\" context."
                   % (len(operations), self.config["owner"], self.config["project"], agent_id)
      }
    else:
      return super(Client, self).add_operations(agent_id, operations)

  def add_operations_bulk(self, payload):
    """Add operations to a group of agents.

    :param list payload: contains the informations necessary for the action.
    It's in the form [{"id": agent_id, "operations": operations}]
    With id that is an str containing only characters in "a-zA-Z0-9_-"
    and must be between 1 and 36 characters. It must referenced an
    existing agent.
    With operations either a list of dict or a DataFrame that has
    the form given in the craftai documentation and the configuration of
    the agent.

    :return: list of agents containing a message about the added
    operations.
    :rtype: list of dict.

    :raises CraftAiBadRequestError: if all of the ids are invalid or
    referenced non existing agents or one of the operations is invalid.
    """
    # Check all ids, raise an error if all ids are invalid
    valid_indices, _, _ = self._check_agent_id_bulk(payload, check_serializable=False)
    valid_payload = [payload[i] for i in valid_indices]

    new_payload = []
    for agent in valid_payload:
      operations = agent["operations"]
      if isinstance(operations, pd.DataFrame):
        if not isinstance(operations.index, pd.DatetimeIndex):
          raise CraftAiBadRequestError("Invalid dataframe given for agent "
                                       "{}, it is not time indexed.".format(agent["id"]))
        if operations.index.tz is None:
          raise CraftAiBadRequestError("tz-naive DatetimeIndex are not supported for "
                                       "agent {}, it must be tz-aware.".format(agent["id"]))

        new_operations = [{
          "timestamp": row.name.value // 10 ** 9, # Timestamp.value returns nanoseconds
          "context": {
            col: row[col] for col in operations.columns if is_valid_property_value(col, row[col])
          }
        } for _, row in operations.iterrows()]
        new_payload.append({"id": agent["id"], "operations": new_operations})
      elif isinstance(operations, list):
        # Check if the operations are serializable
        json.dumps([agent])
        new_payload.append({"id": agent["id"], "operations": operations})
      else:
        raise CraftAiBadRequestError("The operations are not put in a DataFrame or a list"
                                     "of dict form for the agent {}.".format(agent["id"]))

    return super(Client, self).add_operations_bulk(new_payload)

  def get_operations_list(self, agent_id, start=None, end=None):
    operations_list = super(Client, self).get_operations_list(agent_id, start, end)
    return pd.DataFrame(
      [operation["context"] for operation in operations_list],
      index=pd.to_datetime([operation["timestamp"] for operation in operations_list],
                           unit="s").tz_localize("UTC")
    )

  def get_state_history(self, agent_id, start=None, end=None):
    state_history = super(Client, self).get_state_history(agent_id, start, end)

    return pd.DataFrame(
      [state["sample"] for state in state_history],
      index=pd.to_datetime([state["timestamp"] for state in state_history],
                           unit="s").tz_localize("UTC")
    )

  @staticmethod
  def decide_from_contexts_df(tree, contexts_df):
    if isinstance(contexts_df, pd.DataFrame):
      if not isinstance(contexts_df.index, pd.DatetimeIndex):
        raise CraftAiBadRequestError("Invalid dataframe given, it is not time indexed.")
      if contexts_df.index.tz is None:
        raise CraftAiBadRequestError("""tz-naive DatetimeIndex are not supported,
                                     it must be tz-aware.""")
    else:
      raise CraftAiBadRequestError("Invalid data given, it is not a DataFrame.")
    return Interpreter.decide_from_contexts_df(tree, contexts_df)
