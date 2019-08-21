import os
import sys
import argparse
import importlib


NO_RECIPE_MODULE_ERROR = """\
Module 'recipes' not found.

You can either:

    1. Enter the directory where the `recipes` module is located.
    2. Add it's parent folder to PYTHONPATH.
    3. Point to the recipes module using the `--recipes` argument.
"""


HELP = """\
rr [-h] [--recipes RECIPES] COMMAND

Error: {error}

Recipe runner.

optional arguments:
  -h, --help         show this help message and exit
  --recipes RECIPES  Path to the recipes module.
"""


def print_help_and_exit(error):
    print(HELP.format(error=error))
    sys.exit(1)


def create_parser():
    parser = argparse.ArgumentParser(description="Recipe runner.")
    parser.add_argument("--recipes")
    return parser


def main():
    parser = create_parser()
    ns, rest = parser.parse_known_args()
    if ns.recipes is not None:
        recipes = os.path.abspath(ns.recipes)
        # Check if the folder exists.
        if not os.path.isdir(recipes):
            print_help_and_exit(f"Recipes folder not found: {recipes}")
        # If it exists add it's parent folder to PYTHONPATH
        sys.path.insert(0, os.path.dirname(recipes))
        sys.argv[1:] = rest
    else:
        # Add current working directory to the pythonpath if it's not already
        # added.
        cwd = os.getcwd()
        if cwd not in sys.path:
            sys.path.insert(0, cwd)

    # Try to import recipes
    try:
        recipes = importlib.import_module("recipes")
        cli = getattr(recipes, "cli")
        cli()
    except ModuleNotFoundError as e:
        print_help_and_exit(
            NO_RECIPE_MODULE_ERROR if e.name == "recipes" else e.msg
        )


if __name__ == "__main__":
    main()
