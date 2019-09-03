import attr
import json
from typing import Any, Dict, FrozenSet, NewType, Optional, Tuple

from mypy_extensions import TypedDict

from r2c.lib.versioned_analyzer import VersionedAnalyzer, VersionedAnalyzerJson

AnalyzerParameters = NewType("AnalyzerParameters", Dict[str, str])


class SpecifiedAnalyzerJson(TypedDict):
    versionedAnalyzer: VersionedAnalyzerJson
    parameters: AnalyzerParameters


def default_parameters(
    param: Optional[AnalyzerParameters]
) -> FrozenSet[Tuple[str, str]]:
    return frozenset(param.items()) if param else frozenset()


@attr.s(auto_attribs=True, frozen=True)
class SpecifiedAnalyzer:
    """
        Class to represent a specific instance of an analyzer. This includes
        any parameters.

        Contains all necessary information to run an analyzer minus the target of analysis
    """

    versioned_analyzer: VersionedAnalyzer
    # We need to use frozen sets because otherwise we can't really hash this,
    # since dicts are unhashable.
    _parameters: FrozenSet = attr.ib(converter=default_parameters, default=None)

    @property
    def parameters(self) -> AnalyzerParameters:
        return AnalyzerParameters(dict(self._parameters))

    @classmethod
    def from_json_str(cls, json_str: str) -> "SpecifiedAnalyzer":
        obj = json.loads(json_str)
        return cls.from_json(obj)

    @classmethod
    def from_json(cls, json_obj: Dict[str, Any]) -> "SpecifiedAnalyzer":
        if "parameters" in json_obj:
            parameters = AnalyzerParameters(json_obj["parameters"])
        else:
            parameters = AnalyzerParameters({})
        va = VersionedAnalyzer.from_json(json_obj["versionedAnalyzer"])
        return cls(va, parameters)

    def to_json(self) -> SpecifiedAnalyzerJson:
        return {
            "versionedAnalyzer": self.versioned_analyzer.to_json(),
            "parameters": self.parameters,
        }
