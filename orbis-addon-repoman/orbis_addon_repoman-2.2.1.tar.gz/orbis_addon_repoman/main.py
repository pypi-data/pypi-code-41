# -*- coding: utf-8 -*-

import os
import time
import importlib

from orbis_addon_repoman import config
from orbis_eval.libs.decorators import clear_screen
from orbis_eval.core.base import AddonBaseClass


class Main(AddonBaseClass):
    """docstring for Repoman"""

    def __init__(self):
        super(AddonBaseClass, self).__init__()
        self.addon_path = os.path.realpath(__file__).replace("main.py", "")

    @clear_screen()
    def run(self):
        self.start_menu()
        self.select()

    @clear_screen()
    def start_menu(self):
        print("\nWelcome to Repoman!")
        print("What would you like to download?")
        for number, item in config.start_menu_options.items():
            print(f"[{number}]:\t {item}")

    def select(self):
        choice = config.start_menu_options.get(input("-> "), None)

        if choice:
            module_path = f"orbis_addon_repoman.{choice.lower()}"
            imported_module = importlib.import_module(module_path)
            imported_module.Main(self.addon_path).run()
        else:
            print("Not implemented yet")
            time.sleep(4)
            self.start_menu()
