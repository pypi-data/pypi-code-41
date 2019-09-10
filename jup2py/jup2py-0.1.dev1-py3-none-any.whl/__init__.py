from .jup2pylib import jup2py
import sys
import argparse

#*********GLOBAL CONFIG **************
name = "jup2py"
__description__ = "Jup2Py :- Simple way to convert your Jupyter Notebook to .py"
__version__ = "0.1.dev1"
__all__ = [jup2py, __description__]
# ************************************

print(__description__)
print("Please make sure that you have saved the Notebook before running Jup2Py")


def main(argv):
    # handling argparse
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument("-v",
                        "--version",
                        help="Jup2Py Version",
                        action="store_true")
    parser.add_argument("-i",
                        "--input",
                        help="Input Jupyter Notebook to be converted to .py file",
                        type=str)
    parser.add_argument("-o",
                        "--output",
                        help="[Optional]: Output python file name and location",
                        type=str)
    args = parser.parse_args(argv[1:])
    if args.version:
        print(f"Jup2Py {__version__}")
        return 0

    if args.input is None or not args.input.endswith(".ipynb"):
        print("Please enter input jupyter notebook path with --input flag")
        return 0
    else:
        jup2py(jup_filename=args.input, py_filename=args.output)


def run_main():
    try:
        sys.exit(main(sys.argv))
    except Exception as e:
        print("Something went wrong - ", end=" ")
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    run_main()
