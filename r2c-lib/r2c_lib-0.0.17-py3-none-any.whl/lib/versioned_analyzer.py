import attr
import json
from typing import NewType

from mypy_extensions import TypedDict
from semantic_version import Version

from r2c.lib.constants import ECR_URL

AnalyzerName = NewType("AnalyzerName", str)

VersionedAnalyzerJson = TypedDict(
    "VersionedAnalyzerJson", {"name": str, "version": str}
)


@attr.s(auto_attribs=True, frozen=True)
class VersionedAnalyzer:
    """
        Class to represent an analyzer and resolved version
    """

    name: AnalyzerName
    version: Version

    @property
    def image_id(self) -> str:
        """
            ECR Tag of a Versioned Analyzer
        """
        if "/" in self.name:
            return f"{ECR_URL}/massive-{str(self.name)}:{str(self.version)}"
        # HACK: old legacy java-style names (tracked in https://github.com/returntocorp/echelon-backend/issues/2486)
        return f"{ECR_URL}/analyzer/{str(self.name)}:{str(self.version)}"

    @classmethod
    def from_image_id(cls, image_id: str) -> "VersionedAnalyzer":
        """
            Return VersionAnalyzer given image_id
        """
        analyzer_name_full, version = image_id.split(":")
        if "massive-" not in analyzer_name_full:
            # HACK: old legacy java-style names (tracked in https://github.com/returntocorp/echelon-backend/issues/2486)
            name = AnalyzerName(analyzer_name_full.split("/")[-1])
        else:
            parts = analyzer_name_full.split("massive-")
            if len(parts) < 2:
                raise Exception(
                    f"Can't parse image ID for full analyzer name: {analyzer_name_full}"
                )

            name = AnalyzerName(parts[1])

        return cls(name, Version(version))

    def to_json(self) -> VersionedAnalyzerJson:
        return {"name": str(self.name), "version": str(self.version)}

    @classmethod
    def from_json_str(cls, json_str: str) -> "VersionedAnalyzer":
        obj = json.loads(json_str)
        return cls.from_json(obj)

    @classmethod
    def from_json(cls, json_obj: VersionedAnalyzerJson) -> "VersionedAnalyzer":
        if "name" not in json_obj or "version" not in json_obj:
            raise Exception(
                f"Can't parse {json_obj} as a versioned analyzer. Need 'name' and 'version' keys."
            )
        return cls(AnalyzerName(json_obj["name"]), Version(json_obj["version"]))

    def __repr__(self):
        return self.name + ":" + str(self.version)


def build_fully_qualified_name(org: str, analyzer_name: str) -> AnalyzerName:
    return AnalyzerName("/".join([org, analyzer_name]))
