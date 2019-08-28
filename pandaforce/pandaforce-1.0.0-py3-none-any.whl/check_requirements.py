import subprocess
import sys

def __install(package):
    """Runs pip installation on passed package name"""
    subprocess.call([sys.executable, "-m", "pip", "install", package])

def __init__():
    hard_dependencies = ("simple_salesforce", "salesforce_reporting", "pandas","requests")
    missing_dependencies = []

    for dependency in hard_dependencies:
        try:
            __import__(dependency)
        except ImportError as e:
            print(dependency,'failed')
            missing_dependencies.append(dependency)

    if len(missing_dependencies) > 0:
        print("Missing required packages {}".format(missing_dependencies))
        response = input('Would you like to install these packages? y/n')
        if response == 'y':
            __install('simple_salesforce')
            __install('salesforce_reporting')
            __install('pandas')
        else:
            raise Exception('sfpack cannot run without required packages {}'.format(missing_dependencies))

__init__()
