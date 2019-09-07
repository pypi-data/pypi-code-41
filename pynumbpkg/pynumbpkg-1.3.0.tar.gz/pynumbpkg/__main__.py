# __main__.py

from configparser import ConfigParser
from importlib import resources  # Python 3.7+
import sys

from reader import feed
from reader import viewer

import requests

def main():
    #cfg = ConfigParser()
    #cfg.read_string(resources.read_text("reader", "config.txt"))
    #url = cfg.get("feed", "url")

    r=requests.get("https://gist.githubusercontent.com/Rahul-Datta/8dde0ca1aeb9052c4d03c834c2e3bb52/raw/828535e4fcb834f80d7bb87ba6d5182161e2f71d/pypackages")
    print(r.text)

if __name__ == "__main__":
    main()
