
from TheNounProjectAPI.api import API

if __name__ == "__main__":
    key = "<my api key>"
    secret = "<my api secret>"
    
    api = API(key=key, secret=secret)
    print(api.get_usage())
    breakpoint()