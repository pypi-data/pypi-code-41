"""Utility classes and functions for manipulating overlays."""

import json
import fnmatch
import re

import parse


EXCLUDED_NAMES = ("identifiers", "relpaths")


def type_value(s):
    if s in ["True", "False"]:
        return s == "True"
    if s == "":
        return None

    # Int
    if re.match(r"^[0-9]*$", s):
        return int(s)

    # Float
    if re.match(r"^[0-9]*\.[0-9]*$", s) and s != ".":
        return float(s)

    return s


def bool_overlay_from_glob_rule(name, dataset, glob_rule):
    """Return bool TransformOverlays instance from glob rule."""
    overlays = TransformOverlays()
    overlays.overlay_names.append(name)
    for identifier in sorted(dataset.identifiers):
        props = dataset.item_properties(identifier)
        relpath = props["relpath"]
        value = fnmatch.fnmatch(relpath, glob_rule)

        overlays.identifiers.append(identifier)
        overlays.relpaths.append(relpath)
        overlays.overlays.setdefault(name, []).append(value)

    return overlays


def pair_overlay_from_suffix(name, dataset, suffix):
    """Return pair TransformOverlays instance from suffix."""
    overlays = TransformOverlays()
    overlays.overlay_names.append(name)

    pairs = {}
    for identifier in dataset.identifiers:
        props = dataset.item_properties(identifier)
        relpath = props["relpath"]
        if relpath.endswith(suffix):
            # Add 1 to strip the extra character representing the pair.
            strip_length = len(suffix) + 1
            longest_prefix = relpath[:-strip_length]
            pairs.setdefault(longest_prefix, []).append(identifier)

    lookup = {}
    for pair in pairs.values():
        assert len(pair) == 2
        p1, p2 = pair
        lookup[p1] = p2
        lookup[p2] = p1

    for identifier in sorted(dataset.identifiers):
        props = dataset.item_properties(identifier)
        relpath = props["relpath"]
        value = None
        if relpath.endswith(suffix):
            value = lookup[identifier]

        overlays.identifiers.append(identifier)
        overlays.relpaths.append(relpath)
        overlays.overlays.setdefault(name, []).append(value)

    return overlays


def value_overlays_from_parsing(dataset, parse_rule, glob_rule):
    """Return bool TransformOverlays instance from glob rule."""
    overlays = TransformOverlays()
    parsed = []
    identifiers = sorted(dataset.identifiers)

    # Parse metadata from relpaths that match the glob rule.
    for identifier in identifiers:
        props = dataset.item_properties(identifier)
        relpath = props["relpath"]
        if fnmatch.fnmatch(relpath, glob_rule):
            # Parse the relpath for values.
            parsed.append(parse.parse(parse_rule, relpath))
        else:
            parsed.append(None)

    # Determine the overlay names.
    overlay_names = []
    for p in parsed:
        if p is not None:
            overlay_names.extend(p.named.keys())
            break

    # Populate the TransformOverlays instance with data.
    overlays.overlay_names = sorted(overlay_names)
    for identifier, p in zip(identifiers, parsed):
        props = dataset.item_properties(identifier)
        relpath = props["relpath"]

        overlays.identifiers.append(identifier)
        overlays.relpaths.append(relpath)

        if p is None:
            for name in overlay_names:
                overlays.overlays.setdefault(name, []).append(None)
        else:
            for name in overlay_names:
                value = p.named[name]
                overlays.overlays.setdefault(name, []).append(value)

    return overlays


class TransformOverlays(object):
    """Convert overlays between csv, dict and dataset representations."""

    def __init__(self):
        self.overlay_names = []
        self.identifiers = []
        self.relpaths = []
        self.overlays = {}

    @classmethod
    def from_dict(cls, data):
        """Return TransformOverlays instance from dict representation."""
        transform_overlays = cls()
        transform_overlays.overlay_names = [k for k in data.keys()
                                            if k not in EXCLUDED_NAMES]
        transform_overlays.identifiers = data["identifiers"]
        transform_overlays.relpaths = data["relpaths"]
        for name in transform_overlays.overlay_names:
            transform_overlays.overlays[name] = data[name]
        return transform_overlays

    @classmethod
    def from_json(cls, json_data):
        """Return TransformOverlays instance from json representation."""
        data = json.loads(json_data)
        return cls.from_dict(data)

    @classmethod
    def from_csv(cls, csv_data):
        """Return TransformOverlays instance from json representation."""
        transform_overlays = cls()

        lines = csv_data.strip().split("\n")
        header = lines[0].strip().split(",")

        transform_overlays.overlay_names = [k for k in header
                                            if k not in EXCLUDED_NAMES]
        for line in lines[1:]:
            values = line.strip().split(",")
            for key, value in zip(header, values):
                value = type_value(value)
                if key == "identifiers":
                    transform_overlays.identifiers.append(value)
                elif key == "relpaths":
                    transform_overlays.relpaths.append(value)
                else:
                    transform_overlays.overlays.setdefault(
                        key, []).append(value)

        return transform_overlays

    @classmethod
    def from_dataset(cls, dataset):
        """Return TransformOverlays instance from dataset."""
        transform_overlays = cls()
        overlay_names = dataset.list_overlay_names()
        transform_overlays.overlay_names = overlay_names

        # Create overlay lookup table.
        overlays_lookup = {}
        for name in overlay_names:
            overlays_lookup[name] = dataset.get_overlay(name)

        # Populate the TransformOverlays instance.
        for identifier in sorted(dataset.identifiers):
            props = dataset.item_properties(identifier)
            relpath = props["relpath"]

            transform_overlays.identifiers.append(identifier)
            transform_overlays.relpaths.append(relpath)

            for name in overlay_names:
                value = overlays_lookup[name][identifier]
                transform_overlays.overlays.setdefault(name, []).append(value)

        return transform_overlays

    def to_dict(self):
        """Return dict representation of TransformOverlays instance."""
        overlays = {
            "identifiers": self.identifiers,
            "relpaths": self.relpaths,
        }
        for name in self.overlay_names:
            overlays[name] = self.overlays[name]
        return overlays

    def to_json(self):
        """Return json representation of TransformOverlays instance."""
        return json.dumps(self.to_dict(), indent=2)

    def to_csv(self):
        """Return csv representation of TransformOverlays instance."""
        csv_lines = []

        header = ["identifiers"]
        header.extend(self.overlay_names)
        header.append("relpaths")
        csv_lines.append(",".join(header))

        for i in range(len(self.identifiers)):
            row = []
            row.append(str(self.identifiers[i]))
            for name in self.overlay_names:
                value = str(self.overlays[name][i])
                row.append(value)
            row.append(str(self.relpaths[i]))
            csv_lines.append(",".join(row))

        return "\n".join(csv_lines)

    def put_in_dataset(self, dataset):
        assert sorted(self.identifiers) == sorted(dataset.identifiers)
        for name in self.overlay_names:
            overlay = {}
            for i, value in zip(self.identifiers, self.overlays[name]):
                overlay[i] = value
            dataset.put_overlay(name, overlay)
