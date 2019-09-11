import etcd3
import json
import queue
import copy

from collections import namedtuple
from dataclasses import dataclass

PseudoEtcdMeta = namedtuple("PseudoEtcdMeta", ["key"])


@dataclass(init=False)
class EtcdEntry:
    key: str
    value: str
    
    def __init__(self, meta, value, value_in_json=False):
        self.key = meta.key.decode("utf-8")
        self.value = value.decode("utf-8")
        
        if value_in_json:
            try:
                self.value = json.loads(self.value)
            except json.JSONDecodeError as e:
                print(f"Json Error: {e}, value={value}")


class Etcd3Wrapper:
    def __init__(self, *args, **kwargs):
        self.client = etcd3.client(*args, **kwargs)
    
    def get(self, *args, value_in_json=False, **kwargs):   
        _value, _key = self.client.get(*args, **kwargs)
        if _key is None or _value is None:
            return None
        return EtcdEntry(_key, _value, value_in_json=value_in_json)
    
    def put(self, *args, value_in_json=False, **kwargs):
        _key, _value = args
        if value_in_json:
            _value = json.dumps(_value)

        if not isinstance(_key, str):
            _key = _key.decode("utf-8")

        return self.client.put(_key, _value, **kwargs)

    def get_prefix(self, *args, value_in_json=False, **kwargs):
        r = self.client.get_prefix(*args, **kwargs)
        for entry in r:
            e = EtcdEntry(*entry[::-1], value_in_json=value_in_json)
            if e.value:
                yield e

    def watch_prefix(self, key, timeout=0, value_in_json=False):
        timeout_event = EtcdEntry(PseudoEtcdMeta(key=b"TIMEOUT"),
                                  value=str.encode(json.dumps({"status": "TIMEOUT",
                                                               "type": "TIMEOUT"})),
                                  value_in_json=value_in_json)

        event_queue = queue.Queue()

        def add_event_to_queue(event):
            for e in event.events:
                if e.value:
                    event_queue.put(EtcdEntry(e, e.value, value_in_json=value_in_json))

        self.client.add_watch_prefix_callback(key, add_event_to_queue)

        while True:
            try:
                while True:
                    v = event_queue.get(timeout=timeout)
                    yield v
            except queue.Empty:
                event_queue.put(copy.deepcopy(timeout_event))


class PsuedoEtcdEntry(EtcdEntry):
    def __init__(self, key, value, value_in_json=False):
        super().__init__(PseudoEtcdMeta(key=key.encode("utf-8")), value, value_in_json=value_in_json)
