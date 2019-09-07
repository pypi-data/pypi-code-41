import unittest
from typing import Dict, List, Tuple

from symmetry.common.typing import json_schema


class WeightedRandom:
    name = 'WeightedRandom'
    weights: Dict[str, float] = dict()


class ReactiveAutoscaling:
    name = 'ReactiveAutoscaling'

    metric: str = 'cpu'
    th_up: float = 80
    th_down: float = 25
    cooldown: float = 20
    window_length: int = 10


class ListContainer:
    name: str
    nrs: List[int]


class TupleContainer:
    name: str
    tup: Tuple[int, List[str], bool]


class TestTyping(unittest.TestCase):
    def test_json_schema(self):
        schema = {'type': 'string'}
        self.assertEqual(json_schema(str), schema)

        schema = {'type': 'integer'}
        self.assertEqual(json_schema(int), schema)

        schema = {'type': 'object', 'properties': {
            'name': {'type': 'string'},
            'nrs': {'type': 'array', 'items': {'type': 'integer'}}
        }}
        self.assertEqual(json_schema(ListContainer), schema)

        schema = {'type': 'object', 'properties': {
            'name': {'type': 'string'},
            'tup': {'type': 'array', 'items': [
                {'type': 'integer'}, {'type': 'array', 'items': {'type': 'string'}}, {'type': 'boolean'}
            ]}
        }}
        self.assertEqual(json_schema(TupleContainer), schema)

        schema = {'type': 'object', 'properties': {
            'weights': {'type': 'object', 'additionalProperties': {'type': 'number'}}
        }}
        self.assertEqual(json_schema(WeightedRandom), schema)

        schema = {'type': 'object', 'properties': {
            'metric': {'type': 'string'},
            'th_up': {'type': 'number'},
            'th_down': {'type': 'number'},
            'cooldown': {'type': 'number'},
            'window_length': {'type': 'integer'}
        }}
        self.assertEqual(json_schema(ReactiveAutoscaling), schema)
