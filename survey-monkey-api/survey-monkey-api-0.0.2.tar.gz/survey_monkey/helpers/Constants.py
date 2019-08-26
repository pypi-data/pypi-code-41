import os

from survey_monkey import ROOT

DEFAULT_VERSION = "v3"
DEFAULT_ENDPOINTS_FILE_PATH = os.path.join(ROOT, "endpoints.json")
DEFAULT_ADDRESS = "https://api.surveymonkey.net"

PARAMETER_REGEX = r"{(\w+)}"