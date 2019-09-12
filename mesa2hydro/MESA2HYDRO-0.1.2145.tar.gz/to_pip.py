#!/usr/bin/env python

import subprocess

subprocess.call("rm dist/*tar* ", shell =True)
subprocess.call("./setup.py sdist", shell=True)
subprocess.call("twine upload --verbose dist/*", shell=True)