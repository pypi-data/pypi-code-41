import os
import json
import sqlparse
import time
import glob

import networkx as nx

from copy import deepcopy
from networkx.readwrite import json_graph
from pathlib import Path
from pyhocon import ConfigFactory
from typing import Dict, List

from meltano.core.sql.design_helper import PypikaJoinExecutor
from meltano.core.project import Project
from meltano.core.plugin.model import Package
from meltano.core.utils import encode_id_from_file_path, slugify, find_named


class MeltanoAnalysisFileParserError(Exception):
    def __init__(self, message, file_name):
        self.message = message
        self.file_name = file_name
        super().__init__(f"{file_name}: {message}")


class MeltanoAnalysisFileParserMissingTableError(MeltanoAnalysisFileParserError):
    def __init__(self, field, your_choice, cls, file_name):
        message = (
            f'Missing accompanying table "{your_choice}" in "{field}" field in {cls}'
        )
        super().__init__(message, file_name)


class MeltanoAnalysisMissingTopicFilesError(MeltanoAnalysisFileParserError):
    def __init__(self, message):
        super().__init__(message, "topic file")


class MeltanoAnalysisFileParserUnacceptableChoiceError(MeltanoAnalysisFileParserError):
    def __init__(self, field, your_choice, acceptable_choices, cls, file_name):
        quoted_choices = [f'"{a}"' for a in acceptable_choices]
        message = f"Unacceptable choice for field {field}. You wrote \"{your_choice}\". Acceptable choices are: {', '.join(quoted_choices)}"
        super().__init__(message, file_name)


class MeltanoAnalysisFileParserMissingFieldsError(MeltanoAnalysisFileParserError):
    def __init__(self, fields, cls, file_name):
        field = "field" if len(fields) == 1 else "fields"
        message = f"Missing {field} in {cls}: \"{', '.join(fields)}\""
        super().__init__(message, file_name)


class MeltanoAnalysisInvalidJoinDependencyError(MeltanoAnalysisFileParserError):
    def __init__(self, field, cls, file_name):
        message = f'Invalid join dependency for join {cls} in in field "{field}"'
        super().__init__(message, file_name)


class MeltanoAnalysisFileParser:
    def __init__(self, project: Project):
        self.project = project
        self._output_dir = self.project.root_dir("model")
        self.topics = []
        self.tables = []
        self.packaged_topics = []
        self.packaged_tables = []
        self.required_topic_properties = ["name", "connection", "label", "designs"]
        self.required_design_properties = ["from", "label", "description"]
        self.required_join_properties = ["sql_on", "relationship"]
        self.required_table_properties = ["sql_table_name", "columns"]
        self.join_relationship_types = [
            "one_to_one",
            "one_to_many",
            "many_to_one",
            "many_to_many",
        ]
        self.project = Project()

    def uses_accepted_choice(self, choices, choice):
        return choice in choices

    def missing_properties(self, properties, properties_dict):
        properties_copy = properties.copy()
        for prop in properties_dict:
            try:
                property_index = properties_copy.index(prop)
                del properties_copy[property_index]
            except ValueError as e:
                continue
        return properties_copy

    def parse_m5o_file(self, file_path):
        try:
            parsed = ConfigFactory.parse_file(file_path)
            parsed["_file_path"] = str(file_path)
            return parsed
        except Exception as e:
            raise MeltanoAnalysisFileParserError(str(e), str(file_path.parts[-1]))

    def generate_join_graph_for_node(self, graph, design, source_name, joins):
        remaining_joins = []
        check_against = []

        for join in joins:
            join_executor = None
            if "executor" in join:
                join_executor = join["executor"]
            else:
                join_executor = join["executor"] = PypikaJoinExecutor(design, join)
                join_executor.visit(sqlparse.parse(join["sql_on"])[0])

            # the `table` identifier here represent either:
            #   - Design name
            #   - Join name
            left_join_candidate = join_executor.comparison_fields.left.table
            right_join_candidate = join_executor.comparison_fields.right.table

            if left_join_candidate == source_name:
                check_against.append(right_join_candidate)

                # that means we must add the `right` join
                graph.add_node(right_join_candidate)
                graph.add_edge(left_join_candidate, right_join_candidate)
            elif right_join_candidate == source_name:
                check_against.append(left_join_candidate)

                # that means we must add the `left` join
                graph.add_node(left_join_candidate)
                graph.add_edge(right_join_candidate, left_join_candidate)
            else:
                # both `left` & `right` are joins
                remaining_joins.append(join)

        # recurse through the remaining joins
        for check in check_against:
            self.generate_join_graph_for_node(graph, design, check, remaining_joins)

    def graph_design(self, design):
        # The `base` table should always be part of the graph
        # base_table = design["related_table"]["name"]
        source_name = design["name"]

        graph = nx.DiGraph()
        graph.add_node(source_name)
        joins = deepcopy(design.get("joins", []))

        self.generate_join_graph_for_node(graph, design, source_name, joins)
        return json_graph.node_link_data(graph)

    def graph_topic(self, topic):
        for design in topic["designs"]:
            design_graph = self.graph_design(design)
            design["graph"] = design_graph

        return topic

    def compile(self, topics):
        indices = {}
        for topic in topics:
            compiled_file_name = f"{topic['name']}.topic.m5oc"
            compiled_file_path = self._output_dir.joinpath(compiled_file_name)
            indices[topic["name"]] = {"designs": [e["name"] for e in topic["designs"]]}
            topic = self.graph_topic(topic)

            with compiled_file_path.open("w") as compiled_topic:
                json.dump(topic, compiled_topic)

        # index file
        index_file_path = self._output_dir.joinpath("topics.index.m5oc")
        with index_file_path.open("w") as index_file:
            index_file.write(json.dumps(indices))

    def parse_packages(self):
        for package in self.packages():
            if not package.topics and package.tables:
                raise MeltanoAnalysisMissingTopicFilesError(
                    f"Missing topic file(s) for package {package}"
                )

            for table in package.tables:
                conf = self.parse_m5o_file(table)
                parsed_table = self.table(conf, table.name)
                self.tables.append(parsed_table)

            for topic in package.topics:
                conf = self.parse_m5o_file(topic)
                parsed_topic = self.topic(conf, topic.name)
                self.packaged_topics.append(parsed_topic)

        return self.packaged_topics

    def parse(self):
        models = self.project.root_dir("model")
        self.m5o_tables = list(models.glob("*.table.m5o"))
        self.m5o_topics = list(models.glob("*.topic.m5o"))
        if not self.m5o_topics and self.m5o_tables:
            raise MeltanoAnalysisMissingTopicFilesError("Missing topic file(s)")

        for table in self.m5o_tables:
            conf = self.parse_m5o_file(table)
            parsed_table = self.table(conf, table.name)
            self.tables.append(parsed_table)

        for topic in self.m5o_topics:
            conf = self.parse_m5o_file(topic)
            parsed_topic = self.topic(conf, topic.name)
            self.topics.append(parsed_topic)

        return self.topics

    def topic(self, ma_file_topic_dict, file_name):
        temp_topic = {}
        missing_properties = self.missing_properties(
            self.required_topic_properties, ma_file_topic_dict
        )

        if missing_properties:
            raise MeltanoAnalysisFileParserMissingFieldsError(
                missing_properties, "topic", file_name
            )

        for prop_name, prop_def in ma_file_topic_dict.items():
            temp_topic[prop_name] = prop_def
            if prop_name == "designs":
                temp_topic[prop_name] = self.designs(prop_def, file_name)

        return temp_topic

    def table_conf_by_name(self, table_name, cls, prop, file_name):
        try:
            return find_named(self.tables, table_name)
        except StopIteration as e:
            raise MeltanoAnalysisFileParserMissingTableError(
                prop, table_name, cls, file_name
            )

    def designs(self, ma_file_designs_dict, file_name):
        topic_designs = []
        for design_name, design_def in ma_file_designs_dict.items():
            temp_design = {}
            temp_design["name"] = design_name
            missing_properties = self.missing_properties(
                self.required_design_properties, design_def
            )
            if missing_properties:
                raise MeltanoAnalysisFileParserMissingFieldsError(
                    missing_properties, "design", file_name
                )

            for prop_name, prop_def in design_def.items():
                temp_design[prop_name] = prop_def
                if prop_name == "from":
                    temp_design["related_table"] = self.table_conf_by_name(
                        temp_design[prop_name], "design", prop_name, file_name
                    )
                if prop_name == "joins":
                    temp_design[prop_name] = self.joins(prop_def, file_name)

            topic_designs.append(temp_design)

        return topic_designs

    def joins(self, ma_file_joins_dict, file_name):
        design_joins = []
        for join_name, join_def in ma_file_joins_dict.items():
            temp_join = {}
            temp_join["name"] = join_name
            related_table_name = join_def.get("from", join_name)
            temp_join["related_table"] = self.table_conf_by_name(
                related_table_name, "join", "name", file_name
            )
            missing_properties = self.missing_properties(
                self.required_join_properties, join_def
            )
            if missing_properties:
                raise MeltanoAnalysisFileParserMissingFieldsError(
                    missing_properties, "join", file_name
                )

            for prop_name, prop_def in join_def.items():
                temp_join[prop_name] = prop_def
                if prop_name == "relationship":
                    uses_accepted_choices = self.uses_accepted_choice(
                        self.join_relationship_types, prop_def
                    )
                    if not uses_accepted_choices:
                        raise MeltanoAnalysisFileParserUnacceptableChoiceError(
                            prop_name,
                            prop_def,
                            self.join_relationship_types,
                            "join",
                            file_name,
                        )

            design_joins.append(temp_join)

        return design_joins

    def table(self, table_file, file_name):
        temp_table = {}
        missing_properties = self.missing_properties(
            self.required_table_properties, table_file
        )
        if missing_properties:
            raise MeltanoAnalysisFileParserMissingFieldsError(
                missing_properties, "table", file_name
            )

        for prop_name, prop_def in table_file.items():
            subproperties = ("columns", "aggregates", "timeframes")

            if prop_name in subproperties:
                temp_table[prop_name] = self.name_flatten_dict(prop_def)
            else:
                temp_table[prop_name] = prop_def

        return temp_table

    @classmethod
    def name_flatten_dict(cls, d: Dict) -> List:
        return [{"name": k, **rest} for k, rest in d.items()]

    @staticmethod
    def fill_base_m5o_dict(file, name, file_dict=None):
        if file_dict is None:
            file_dict = {"name": name}

        file_dict["path"] = str(file)
        file_dict["id"] = encode_id_from_file_path(file_dict["path"])
        file_dict["slug"] = slugify(name)
        file_dict["createdAt"] = time.time()
        return file_dict

    def packages(self) -> List[Package]:
        return [
            Package(f.name, self.project)
            for f in self.project.model_dir().iterdir()
            if f.is_dir()
        ]

    @classmethod
    def package_files(cls, package):
        m5oFiles = {
            "topics": {"label": "Topics", "items": []},
            "tables": {"label": "Tables", "items": []},
        }
        for f in package.files:
            basename = os.path.basename(f)
            filename, ext = os.path.splitext(basename)
            if ext != ".m5o":
                continue

            # filename splittext twice occurs due to current *.type.extension convention (two dots)
            filename = f"{package.name}/{filename.lower()}"
            filename, ext = os.path.splitext(filename)
            file_dict = cls.fill_base_m5o_dict(f, filename)
            if ext == ".topic":
                m5oFiles["topics"]["items"].append(file_dict)
            if ext == ".table":
                m5oFiles["tables"]["items"].append(file_dict)

        return m5oFiles
