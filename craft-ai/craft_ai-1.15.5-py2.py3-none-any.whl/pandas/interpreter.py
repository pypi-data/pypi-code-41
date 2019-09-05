import pandas as pd

from .. import Interpreter as VanillaInterpreter, Time
from ..errors import CraftAiNullDecisionError
from .utils import is_valid_property_value, create_timezone_df, format_input

class Interpreter(VanillaInterpreter):
  @staticmethod
  def decide_from_contexts_df(tree, contexts_df):
    bare_tree, configuration, tree_version = VanillaInterpreter._parse_tree(tree)
    interpreter = VanillaInterpreter._get_interpreter(tree_version)

    df = contexts_df.copy(deep=True)

    tz_col = [key for key, value in configuration["context"].items()
              if value["type"] == "timezone"]
    # If a timezone is needed create a timezone dataframe which will
    # store the timezone to use. It can either be the DatetimeIndex
    # timezone or the timezone column if provided.
    if tz_col:
      tz_col = tz_col[0]
      df[tz_col] = create_timezone_df(contexts_df, tz_col).iloc[:, 0]

    predictions_iter = (
      Interpreter.decide_from_row(bare_tree, row, tz_col, configuration, interpreter)
      for row in df.itertuples()
    )
    return pd.DataFrame(predictions_iter, index=df.index)

  @staticmethod
  def decide_from_row(bare_tree, row, tz_col, configuration, interpreter):
    context = {
      index: format_input(value) for index, value in row._asdict().items()
      if is_valid_property_value(index, value)
    }
    time = Time(
      t=row[0].value // 1000000000, # Timestamp.value returns nanoseconds
      timezone=context[tz_col] if tz_col else row[0].tz
    )
    try:
      decision = VanillaInterpreter._decide(
        configuration,
        bare_tree,
        (context, time),
        interpreter
      )

      return {
        "{}_{}".format(output, key): value
        for output, output_decision in decision["output"].items()
        for key, value in output_decision.items()
      }
    except CraftAiNullDecisionError as e:
      return {"error": e.message}
