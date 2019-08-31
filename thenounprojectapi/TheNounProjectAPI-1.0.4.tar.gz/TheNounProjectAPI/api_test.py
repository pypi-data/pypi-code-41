
import os
from TheNounProjectAPI.api import API

if __name__ == "__main__":
    api = API(key=os.environ["TNP_KEY"], secret=os.environ["TNP_SECRET"])
    print(api.get_usage())
    breakpoint()