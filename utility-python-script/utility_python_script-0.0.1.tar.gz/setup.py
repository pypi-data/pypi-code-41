import re
from distutils.core import setup
from setuptools import find_packages

VERSIONFILE="utility_python_script/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

setup(
    name="utility_python_script",
    version=verstr,
    author="eayin2",
    author_email="eayin2@gmail.com",
    packages=find_packages(),
    url="https://github.com/eayin2/utility_python_script",
    description="Utility python scripts",
    install_requires=[
        "gymail",
        "helputils"
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "pulseaudio_switch = utility_python_script.pulseaudio_switch:main",
            "rsync_python_script = utility_python_script.rsync_python_script:main",
        ],
    },
)
