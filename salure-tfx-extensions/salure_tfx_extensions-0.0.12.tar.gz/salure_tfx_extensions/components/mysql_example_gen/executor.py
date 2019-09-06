"""Custom MySQL Component Executor"""

from typing import Any, Dict, List, NamedTuple, Text, Tuple, Iterable
import datetime

import apache_beam as beam
import tensorflow as tf
import pymysql

from google.protobuf import json_format
from tfx import types
from tfx.components.example_gen import base_example_gen_executor
from tfx.proto import example_gen_pb2
from salure_tfx_extensions.proto import mysql_config_pb2


@beam.typehints.with_input_types(Text)
@beam.typehints.with_output_types(beam.typehints.Iterable[Tuple[Text, Text, Any]])
class _ReadMySQLDoFn(beam.DoFn):

    def __init__(self, client: pymysql.Connection):
        self.cursor = client.cursor()

    def process(self, query: Text) -> Iterable[Tuple[Text, Text, Any]]:
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        if rows:
            cols = []
            col_types = []

            for metadata in self.cursor.description:
                cols.append(metadata[0])
                col_types.append(metadata[1])

            for row in rows:
                yield zip(cols, col_types, row)

    def teardown(self):
        if self.cursor:
            self.cursor.close()


def _deserialize_conn_config(conn_config: mysql_config_pb2.MySQLConnConfig) -> pymysql.Connection:
    keys = ['host', 'port', 'user', 'password', 'database']
    params = {}
    for key in keys:
        if conn_config.HasField(key):
            params[key] = conn_config[key]
    return pymysql.connect(**params)


def _row_to_example(row: Iterable[Tuple[Text, Text, Any]]) -> tf.train.Example:
    # TODO: Check what the cursor description output types are
    """Convert DB result row to tf example."""
    feature = {}
    for key, data_type, value in row:
        # TODO: remove print
        print(data_type)
        if value is None:
            feature[key] = tf.train.Feature()
        elif data_type in {'tinyint', 'smallint', 'integer', 'bigint', 'mediumint'}:
            feature[key] = tf.train.Feature(
                int64_list=tf.train.Int64List(value=[value]))
        elif data_type in {'real', 'double', 'decimal'}:
            feature[key] = tf.train.Feature(
                float_list=tf.train.FloatList(value=[value]))
        elif data_type in {'varchar', 'char'}:
            feature[key] = tf.train.Feature(
                bytes_list=tf.train.BytesList(value=[tf.compat.as_bytes(value)]))
        elif data_type in {'timestamp'}:
            value = int(datetime.datetime.fromisoformat(value).timestamp())
            feature[key] = tf.train.Feature(
                int64_list=tf.train.Int64List(value=[value]))
        else:
            # TODO: support more types
            raise RuntimeError(
                'Column type {} is not supported.'.format(data_type))

    return tf.train.Example(features=tf.train.Features(feature=feature))


@beam.ptransform_fn
@beam.typehints.with_input_types(beam.Pipeline)
@beam.typehints.with_output_types(tf.train.Example)
def _MySQLToExample(
        pipeline: beam.Pipeline,
        input_dict: Dict[Text, List[types.Artifact]],
        exec_properties: Dict[Text, any],
        split_pattern: Text) -> beam.pvalue.PCollection:
    conn_config = example_gen_pb2.CustomConfig()
    json_format.Parse(exec_properties['custom_config'], conn_config)
    mysql_config = mysql_config_pb2.MySQLConnConfig()
    conn_config.custom_config.Unpack(mysql_config)

    client = _deserialize_conn_config(mysql_config)

    return (pipeline
            | 'Query' >> beam.Create([split_pattern])
            | 'QueryTable' >> beam.ParDo(_ReadMySQLDoFn(client))
            | 'ToTFExample' >> beam.Map(_row_to_example))


class Executor(base_example_gen_executor.BaseExampleGenExecutor):
    """Generic TFX MySQL executor"""

    def GetInputSourceToExamplePTransform(self) -> beam.PTransform:
        """Returns PTransform for MySQl to TF examples."""
        return _MySQLToExample
