import os
import json
import pathlib
from loguru import logger
from functools import wraps

def write_runtime(runtime):
    try:
        with open(os.getcwd() + "/app.dump", "w") as f:
            return f.write(json.dumps(runtime))
    except:
        return False

def load_runtime():
    try:
        with open(os.getcwd() + "/app.dump", "r") as f:
            return json.loads(f.read())
    except:
        return False
