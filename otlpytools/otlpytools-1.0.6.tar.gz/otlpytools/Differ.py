class Differ:

    # If Key is none, path is top level
    @classmethod
    def diff(cls, actual, expected, ignore_list=[], key="", path=""):
        value_differences = []
        missing_keys = []
        wrong_types = []
        if isinstance(expected, dict):
            for k, value in expected.items():
                if k in ignore_list:
                    continue
                if k not in actual:
                    missing_keys.append({"key": k, "path": path})
                    continue
                p = Differ.get_path(path=path, key=k)
                diffs, missing, wrong_type = Differ.diff(actual=actual[k], expected=value, ignore_list=ignore_list, key=k, path=p)
                value_differences += diffs
                if missing:
                    missing_keys += missing
                wrong_types += wrong_type
        elif isinstance(expected, list):
            if key == "option": # This is a list of check boxes in the frontend
                if len(actual) > 0:
                    if "name" in actual[0]:
                        actual = sorted(actual, key=lambda k: k['name']) 
            for v in actual:
                if key == "option": # This is a list of check boxes in the frontend
                    if "name" in actual[0]:
                        expected = sorted(expected, key=lambda k: k['name']) 
                v_index_in_actual = actual.index(v)
                p = Differ.get_path(path=path, key=key)
                try:
                    diffs, missing, wrong_type = Differ.diff(actual=v, expected=expected[v_index_in_actual], ignore_list=ignore_list, key=key, path=p)
                    value_differences += diffs
                    if missing:
                        missing_keys += missing
                    wrong_types += wrong_type
                except:
                    missing_keys.append({"key": v, "path":path})
        elif isinstance(expected, str) or isinstance(expected, int):
            if key not in ignore_list: # Should be different
                if actual != expected:
                    path = Differ.get_path(path=path, key=key)
                    diff = {
                        "actualValue": actual,
                        "expectedValue": expected,
                        "path": path
                    }
                    value_differences.append(diff)
        else:
            p = Differ.get_path(path=path, key=key)
            wrong_types.append({"type": type(actual).__name__, "path":p})
        return value_differences, missing_keys, wrong_types
    
    @classmethod
    def get_path(cls, path, key):
        keys_in_path = path.split("/")
        if keys_in_path[len(keys_in_path) - 1] != key:
            path = f"{path}/{key}"
        return path
