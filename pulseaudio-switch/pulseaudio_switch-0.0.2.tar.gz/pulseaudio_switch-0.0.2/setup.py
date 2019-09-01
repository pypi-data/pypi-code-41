import re
from distutils.core import setup
from setuptools import find_packages

VERSIONFILE="pulseaudio_switch/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

setup(
    name="pulseaudio_switch",
    version=verstr,
    author="eayin2",
    author_email="eayin2@gmail.com",
    packages=find_packages(),
    url="https://github.com/eayin2/pulseaudio_switch",
    description="pulseaudio_switch",
    install_requires=[],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "pulseaudio_switch = pulseaudio_switch.main:main",
        ],
    },
)
