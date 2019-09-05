import re
import semver

from craftai.errors import CraftAiDecisionError
from craftai.time import Time
from craftai.timezones import get_timezone_key, timezone_offset_in_standard_format
from craftai.interpreter_v1 import InterpreterV1
from craftai.interpreter_v2 import InterpreterV2

class Interpreter(object):

  @staticmethod
  def decide(tree, args):
    bare_tree, configuration, tree_version = Interpreter._parse_tree(tree)
    interpreter = Interpreter._get_interpreter(tree_version)

    return Interpreter._decide(configuration, bare_tree, args, interpreter)

  ####################
  # Internal helpers #
  ####################

  @staticmethod
  def _decide(configuration, bare_tree, args, interpreter):
    if configuration != {}:
      time = None if len(args) == 1 else args[1]
      context_result = Interpreter._rebuild_context(configuration, args[0], time)
      context = context_result["context"]
    else:
      context = Interpreter.join_decide_args(args)
    # Convert timezones as integers into standard +/hh:mm format
    # This should only happen when no time generated value is required
    decide_context = Interpreter._convert_timezones_to_standard_format(configuration,
                                                                       context.copy())

    decision = interpreter.decide(configuration, bare_tree, decide_context)
    decision["context"] = context

    return decision

  @staticmethod
  def _get_interpreter(tree_version):
    if semver.match(tree_version, ">=1.0.0") and semver.match(tree_version, "<2.0.0"):
      return InterpreterV1
    elif semver.match(tree_version, ">=2.0.0") and semver.match(tree_version, "<3.0.0"):
      return InterpreterV2
    else:
      raise CraftAiDecisionError(
        """Invalid decision tree format, "{}" is currently not a valid version.""".
        format(tree_version)
      )

  @staticmethod
  def _rebuild_context(configuration, state, time=None):

    missings = []
    # Model should come from _parse_tree and is assumed to be checked
    # upon already
    output = configuration["output"]
    context = configuration["context"]

    # We should not use the output key(s) to compare against
    configuration_ctx = {
      key: context[key] for (key, value) in context.items() if (key not in output)
    }

    # Check if we need the time object
    to_generate = []

    for prop in configuration_ctx.items():
      prop_name = prop[0]
      prop_attributes = prop[1]
      if prop_attributes["type"] in ["time_of_day", "day_of_week", "day_of_month",
                                     "month_of_year"]:
        # is_generated is at True, we must generate the time for the
        # associated context property
        case_1 = "is_generated" in list(prop_attributes.keys()) and prop[1]["is_generated"]
        # is_generated is not given, by default at True, so we must
        # generate it as well
        case_2 = "is_generated" not in list(prop_attributes.keys())
        if case_1 or case_2:
          to_generate.append(prop_name)

    # Propagate missings properties to next function
    if to_generate:
      # Can't generate from time -> missings properties are errors
      if not isinstance(time, Time):
        # Check for missings properties
        for prop in to_generate:
          if prop not in list(state.keys()):
            missings.append("expected property '{}' is not defined".format(prop))

      # Generate context properties which need to
      else:
        for prop in to_generate:
          state[prop] = time.to_dict()[configuration_ctx[prop]["type"]]

    # Rebuild the context with generated and non-generated values
    context = {
      feature: state.get(feature) for feature, properties in configuration_ctx.items()
    }

    return {
      "context": context,
      "errors": missings
    }

  @staticmethod
  def join_decide_args(args):
    joined_args = {}
    for arg in args:
      if isinstance(arg, Time):
        joined_args.update(arg.to_dict())
      try:
        joined_args.update(arg)
      except TypeError:
        raise CraftAiDecisionError(
          """Invalid context args, the given objects aren't dicts"""
          """ or Time instances."""
        )
    return joined_args

  @staticmethod
  def _convert_timezones_to_standard_format(configuration, context):
    timezone_key = get_timezone_key(configuration["context"])
    if timezone_key:
      context[timezone_key] = timezone_offset_in_standard_format(context[timezone_key])
    return context

  @staticmethod
  def _parse_tree(tree_object):
    # Checking definition of tree_object
    if not isinstance(tree_object, dict):
      raise CraftAiDecisionError("Invalid decision tree format, the given json is not an object.")

    # Checking version existence
    tree_version = tree_object.get("_version")
    if not tree_version:
      raise CraftAiDecisionError(
        """Invalid decision tree format, unable to find the version"""
        """ informations."""
      )

    # Checking version and tree validity according to version
    if re.compile(r"\d+.\d+.\d+").match(tree_version) is None:
      raise CraftAiDecisionError(
        """Invalid decision tree format, "{}" is not a valid version.""".
        format(tree_version)
      )
    elif semver.match(tree_version, ">=1.0.0") and semver.match(tree_version, "<3.0.0"):
      if tree_object.get("configuration") is None:
        raise CraftAiDecisionError(
          """Invalid decision tree format, no configuration found"""
        )
      if tree_object.get("trees") is None:
        raise CraftAiDecisionError(
          """Invalid decision tree format, no tree found."""
        )
      bare_tree = tree_object.get("trees")
      configuration = tree_object.get("configuration")
    else:
      raise CraftAiDecisionError(
        """Invalid decision tree format, {} is not a supported"""
        """ version.""".
        format(tree_version)
      )
    return bare_tree, configuration, tree_version
