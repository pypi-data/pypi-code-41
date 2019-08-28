# -*- coding: utf-8 -*-
import threading


def local_data_mapping():
    local_data = threading.local()

    def add_item_to_local(key_name, creator):
        def store_value_if_not_none():
            val = creator(key_name)
            if val is not None:
                local_data.__mappings[key_name] = val

            return val

        try:
            return local_data.__mappings[key_name]
        except KeyError:
            pass
        except AttributeError:  # first time we enter a value
            local_data.__mappings = {}

        return store_value_if_not_none()

    return add_item_to_local
