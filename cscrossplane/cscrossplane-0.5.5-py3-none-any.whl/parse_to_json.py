import json
import crossplane

def parse_to_json(path):
    dict = crossplane.parse(path)
    return json.dumps(dict)


