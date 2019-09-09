import configparser
from json import dumps


def extract_ini_from_doc(doc):
    """Extracts INI from doc strings."""
    return doc.rsplit("INI")[-1]


def load_config(ini_string):
    """Load config parse from string."""
    # Override lower case key conversion
    config = configparser.RawConfigParser()
    config.optionxform = lambda option: option
    config.read_string(ini_string)
    return config


def format_headers(config):
    """Returns a list of formatted header dictionaries."""
    request_header = []
    try:
        header_items = eval(config["header"])
        for key in header_items:
            header = {
                "key": key,
                "name": key,
                "value": header_items[key],
                "type": "text",
            }
            request_header.append(header)
    except KeyError:
        pass
    return request_header


def format_json_body(config):
    """formats JSON body from config as raw JSON."""
    body = {}
    body["mode"] = "raw"
    body["raw"] = {}
    try:
        body_dict = eval(config["body"])
        for key in body_dict:
            body["raw"][key] = body_dict[key]
        body["raw"] = dumps(body["raw"])
    except KeyError:
        pass
    return body


def format_query_params(request, config):
    """formats query parameters from config and attached to URL."""
    if "query" in config["request"].keys():
        request["request"]["url"]["raw"] += config["request"]["query"]
        request["request"]["url"]["host"] = [request["request"]["url"]["raw"]]
    return request


def add_INI_data(doc, request, config):
    """adds INI elements to atomic request. Returns altered request."""
    body = format_json_body(config["request"])
    request["request"]["body"] = body

    head = format_headers(config["request"])
    request["request"]["header"] = head

    request = format_query_params(request, config)
    request["protocolProfileBehavior"] = {"disableBodyPruning": True}
    return request

