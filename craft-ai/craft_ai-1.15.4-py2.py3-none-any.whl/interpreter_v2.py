import math
import numbers
import six

from craftai.errors import CraftAiDecisionError, CraftAiNullDecisionError
from craftai.operators import OPERATORS, OPERATORS_FUNCTION
from craftai.types import TYPES
from craftai.timezones import is_timezone

_DECISION_VERSION = "2.0.0"

_VALUE_VALIDATORS = {
  TYPES["continuous"]: lambda value: isinstance(value, numbers.Real),
  TYPES["enum"]: lambda value: isinstance(value, six.string_types),
  TYPES["boolean"]: lambda value: isinstance(value, bool),
  TYPES["timezone"]: lambda value: is_timezone(value),
  TYPES["time_of_day"]: lambda value: (isinstance(value, numbers.Real)
                                       and value >= 0 and value < 24),
  TYPES["day_of_week"]: lambda value: (isinstance(value, six.integer_types)
                                       and value >= 0 and value <= 6),
  TYPES["day_of_month"]: lambda value: (isinstance(value, six.integer_types)
                                        and value >= 1 and value <= 31),
  TYPES["month_of_year"]: lambda value: (isinstance(value, six.integer_types)
                                         and value >= 1 and value <= 12)
}

##############################
## Interpreter for V2 Trees ##
##############################

class InterpreterV2(object):

  @staticmethod
  def decide(configuration, bare_tree, context):
    # Check if missing values are handled
    deactivate_missing_values = True
    if configuration.get("deactivate_missing_values", True) is False:
      deactivate_missing_values = False

    InterpreterV2._check_context(configuration, context, deactivate_missing_values)

    decision_result = {}
    decision_result["output"] = {}
    for output in configuration.get("output"):
      output_type = configuration["context"][output]["type"]
      decision_result["output"][output] = InterpreterV2._decide_recursion(bare_tree[output],
                                                                          context,
                                                                          bare_tree[output].get(
                                                                            "output_values"),
                                                                          output_type,
                                                                          deactivate_missing_values,
                                                                          ["0"])
    decision_result["_version"] = _DECISION_VERSION
    return decision_result

  #pylint: disable-msg=too-many-arguments, too-many-locals
  @staticmethod
  def _decide_recursion(node, context, output_values, output_type, deactivate_missing_values, path):
    # If we are on a leaf
    if not (node.get("children") is not None and len(node.get("children"))):
      # We check if a leaf has the key 'prediction' corresponging to a v2 tree
      prediction = node.get("prediction")
      if prediction is None:
        prediction = node

      predicted_value = prediction.get("value")
      if predicted_value is None:
        raise CraftAiNullDecisionError(
          """Unable to take decision: the decision tree has no valid"""
          """ predicted value for the given context.""",
          {"decision_rules": [node.get("decision_rule")]}
        )

      leaf = {
        "predicted_value": predicted_value,
        "confidence": prediction.get("confidence") or 0,
        "decision_rules": [],
        "nb_samples": prediction["nb_samples"],
        "decision_path": "-".join(path)
      }

      distribution = prediction.get("distribution")
      if not isinstance(distribution, list) and distribution.get("standard_deviation"):
        leaf["standard_deviation"] = distribution.get("standard_deviation")
        leaf["min"] = distribution.get("min")
        leaf["max"] = distribution.get("max")
      else:
        leaf["distribution"] = distribution

      return leaf
    # Finding the first element in this node's childrens matching the
    # operator condition with given context
    matching_child_i, matching_child = InterpreterV2._find_matching_child(node,
                                                                          context,
                                                                          deactivate_missing_values)

    # If there is no child corresponding matching the operators then we compute
    # the probabilistic distribution from this node.
    if not matching_child:
      if not deactivate_missing_values:
        return InterpreterV2.compute_distribution(node, output_values, output_type, path)
      prop = node.get("children")[0].get("decision_rule").get("property")
      operand_list = [child["decision_rule"]["operand"] for child in node["children"]]
      decision_rule = [node["decision_rule"]] if not node.get("decision_rule") is None else []
      raise CraftAiNullDecisionError(
        """Unable to take decision: value '{}' for property '{}' doesn't"""
        """ validate any of the decision rules.""".format(context.get(prop), prop),
        {
          "decision_rules": decision_rule,
          "expected_values": operand_list,
          "property": prop,
          "value": context.get(prop)
        }
      )
    # Add the matching child index to the path
    path.append(str(matching_child_i))
    # If a matching child is found, recurse
    try:
      result = InterpreterV2._decide_recursion(matching_child, context, output_values,
                                               output_type, deactivate_missing_values,
                                               path)
    except CraftAiDecisionError as err:
      metadata = err.metadata
      if node.get("decision_rule"):
        metadata["decision_rules"].insert(0, node["decision_rule"])
      raise CraftAiDecisionError(err.message, metadata)

    new_predicates = [{
      "property": matching_child["decision_rule"]["property"],
      "operator": matching_child["decision_rule"]["operator"],
      "operand": matching_child["decision_rule"]["operand"]
    }]

    final_result = {
      "predicted_value": result["predicted_value"],
      "confidence": result["confidence"],
      "decision_rules": new_predicates + result["decision_rules"],
      "nb_samples": result["nb_samples"],
      "decision_path": result["decision_path"]
    }

    if result.get("standard_deviation", None) is not None:
      final_result["standard_deviation"] = result.get("standard_deviation")

    if result.get("min") is not None:
      final_result["min"] = result.get("min")

    if result.get("max") is not None:
      final_result["max"] = result.get("max")

    if result.get("distribution"):
      final_result["distribution"] = result.get("distribution")

    return final_result

  @staticmethod
  def compute_distribution(node, output_values, output_type, path):
    result = InterpreterV2._distribution(node, output_type)
    if output_type == "enum":
      distribution, nb_samples = result
      final_result = {
        "predicted_value": output_values[distribution.index(max(distribution))],
        "distribution": distribution,
        "nb_samples": nb_samples
      }
    else:
      mean_value, nb_samples, standard_deviation = result
      final_result = {
        "predicted_value": mean_value,
        "nb_samples": nb_samples,
        "standard_deviation": standard_deviation
      }
    final_result["decision_rules"] = []
    final_result["confidence"] = None
    final_result["decision_path"] = "-".join(path)

    return final_result

  @staticmethod
  def _distribution(node, output_type):
    # If it is a leaf
    if not (node.get("children") is not None and len(node.get("children"))):
      prediction = node["prediction"]
      value_distribution = prediction["distribution"]
      nb_samples = prediction["nb_samples"]
      # It is a classification problem
      if output_type == "enum":
        return [value_distribution, nb_samples]
      else:
        # It is a regression problem
        predicted_value = prediction.get("value")
        standard_deviation = value_distribution.get("standard_deviation")
        if predicted_value is not None:
          if standard_deviation is not None:
            return [predicted_value, nb_samples, standard_deviation]
          raise CraftAiDecisionError(
            """Unable to take decision: the decision tree has no valid"""
            """ standard deviation for the given context."""
          )
        raise CraftAiDecisionError(
          """Unable to take decision: the decision tree has no valid"""
          """ predicted value for the given context."""
        )
    # If it is not a leaf, we recurse into the children and store
    # the distributions/means and sizes of each child branch.
    def recurse(_child):
      return InterpreterV2._distribution(_child, output_type)
    values_sizes = list(map(recurse, node.get("children")))
    # It is a classification problem
    if output_type == "enum":
      values, sizes = zip(*values_sizes)
      return InterpreterV2.compute_mean_distributions(values, sizes)
    values, sizes, stds = zip(*values_sizes)
    return InterpreterV2.compute_mean_values(values, sizes, stds)

  @staticmethod
  def compute_mean_distributions(values, sizes):
    # Compute the weighted mean of the given array of distributions (array of probabilities).
    # Example, for values = [[ 4, 3, 6 ], [1, 2, 3], [3, 4, 5]], sizes = [1, 2, 1]
    # This function computes ([ 4, 3, 6]*1 + [1, 2, 3]*2 + [3, 4, 5]*6) / (1+2+1) = ...
    total_size = sum(sizes)
    ratio_applied = [[x * size / float(total_size) for x in x_array]
                     for x_array, size in zip(values, sizes)]
    return list(map(sum, zip(*ratio_applied))), total_size

  @staticmethod
  def compute_mean_values(values, sizes, stds=None):
    # Compute the weighted mean of the given array of values.
    # Example, for values = [ 4, 3, 6 ], sizes = [1, 2, 1]
    # This function computes (4*1 + 3*2 + 1*6) / (1+2+1) = 16/4 = 4
    # If no standard deviation array is given, use classical weighted mean formula:
    if stds is None:
      total_size = sum(sizes)
      mean = sum([val * size / float(total_size)
                  for val, size in zip(values, sizes)])
      return mean, total_size
    # Otherwise, to compute the weighted standard deviation the following formula is used:
    # https://math.stackexchange.com/questions/2238086/calculate-variance-of-a-subset
    new_variance = None
    new_mean = None
    new_size = None
    for mean, std, size in zip(values, stds, sizes):
      variance = std * std
      if new_mean is None:
        new_variance = variance
        new_mean = mean
        new_size = size
        continue
      total_size = 1.0 * size + new_size
      if total_size == 0:
        continue
      new_variance = (1.0 / (total_size - 1.0)) * (
        (size - 1.0) * variance
        + (new_size - 1.0) * new_variance
        + (size * new_size / total_size) * (mean - new_mean)**2
      )
      new_mean = (1.0 / total_size) * (size * mean + new_size * new_mean)
      new_size = total_size
    return new_mean, new_size, math.sqrt(new_variance)

  @staticmethod
  def _find_matching_child(node, context, deactivate_missing_values=True):
    for child_index, child in enumerate(node["children"]):
      property_name = child["decision_rule"]["property"]
      operand = child["decision_rule"]["operand"]
      operator = child["decision_rule"]["operator"]
      context_value = context.get(property_name)

      # If there is no context value:
      if context_value is None:
        if deactivate_missing_values:
          raise CraftAiDecisionError(
            """Unable to take decision, property '{}' is missing from the given context.""".
            format(property_name)
          )
      if (not isinstance(operator, six.string_types) or
          not operator in OPERATORS.values()):
        raise CraftAiDecisionError(
          """Invalid decision tree format, {} is not a valid"""
          """ decision operator.""".format(operator)
        )

      if OPERATORS_FUNCTION[operator](context_value, operand):
        return child_index, child
    return None, {}

  @staticmethod
  def _check_context(configuration, context, deactivate_missing_values=True):
    # Extract the required properties (i.e. those that are not the output)
    expected_properties = [
      p for p in configuration["context"]
      if not p in configuration["output"]
    ]

    if deactivate_missing_values:
      # Retrieve the missing properties
      missing_properties = [
        p for p in expected_properties
        if not p in context or context[p] is None
      ]
    else:
      missing_properties = []

    # Validate the values
    bad_properties = [
      p for p in expected_properties
      if not InterpreterV2.validate_property_value(configuration, context, p)
    ]
    if missing_properties or bad_properties:
      missing_properties = sorted(missing_properties)
      missing_properties_messages = [
        "expected property '{}' is not defined"
        .format(p) for p in missing_properties
      ]
      bad_properties = sorted(bad_properties)
      bad_properties_messages = [
        "'{}' is not a valid value for property '{}' of type '{}'"
        .format(context[p], p, configuration["context"][p]["type"]) for p in bad_properties
      ]

      errors = missing_properties_messages + bad_properties_messages

      # deal with missing properties
      if errors:
        message = "Unable to take decision, the given context is not valid: " + errors.pop(0)

        for error in errors:
          message = "".join((message, ", ", error))
        message = message + "."

        metadata = {}
        if bad_properties:
          metadata["badProperties"] = [
            {"property": p, "type": configuration["context"][p]["type"], "value": context[p]}
            for p in bad_properties
          ]
        if missing_properties:
          metadata["missingProperties"] = missing_properties

        raise CraftAiDecisionError(message, metadata)

  @staticmethod
  def validate_property_value(configuration, context, property_name):
    if not property_name in context:
      return False

    if context[property_name] is None:
      return True
    property_def = configuration["context"][property_name]
    property_type = property_def["type"]
    is_optional = property_def.get("is_optional")
    if property_type in _VALUE_VALIDATORS:
      property_value = context[property_name]
      return _VALUE_VALIDATORS[property_type](property_value) or (is_optional
                                                                  and property_value == {})
    return True
