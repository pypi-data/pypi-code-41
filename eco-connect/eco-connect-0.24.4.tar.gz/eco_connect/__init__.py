import os
import requests
from eco_connect.facts_service import FactsService


def validate_credentials():
    username = os.environ.get("ECO_CONNECT_USER", None)
    password = os.environ.get("ECO_CONNECT_PASSWORD", None)
    result = requests.get("https://facts.prod.ecorithm.com/", auth=(username, password))
    if result.status_code == 200:
        print("\033[92mEcorithm credentials succesfully validated!\033[0m")
        return True
    else:
        print("\033[91mEcorithm credentials are not valid!\033[0m")
        return False


if __name__ == "__main__":
    validate_credentials()
