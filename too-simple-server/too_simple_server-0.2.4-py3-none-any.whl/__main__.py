"""Run server as module"""
from argparse import ArgumentParser

from too_simple_server.configuration import DEFAULT_CFG_PATH
from too_simple_server.run import main

AGP = ArgumentParser(description="Mock server with simple DB interactions")
AGP.add_argument("--debug", action="store_true", default=None)
AGP.add_argument("--config", help=f"Configuration file to be used, '{DEFAULT_CFG_PATH}' by default",
                 default=DEFAULT_CFG_PATH)
AGP.add_argument("--no-wsgi", action="store_true", default=False)
AGP.add_argument("action", default="start", choices=["start", "stop"])
ARGS = AGP.parse_args()

main(ARGS.action, ARGS.debug, ARGS.config, ARGS.no_wsgi)
