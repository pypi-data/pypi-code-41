from setuptools import setup, find_packages
from pathlib import Path
from setuptools.command.install import install
import sys
import os

root_dir = Path(__file__).parent
requirements = Path(root_dir, "requirements.txt")
requirements_dev = Path(root_dir, "requirements-dev.txt")
packages = find_packages(where=root_dir, exclude=["tests*"])

VERSION = "0.5.1"


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""

    description = "verify that the git tag matches our version"

    def run(self):
        tag = os.getenv("CURRENT_TAG")

        if tag != f"v{VERSION}":
            info = "Git tag: {0} does not match the version of this library: {1}".format(
                tag, VERSION
            )
            sys.exit(info)


def list_requirements(file_name):
    return [line.strip() for line in open(file_name)]


with open("README.md", "r") as readable:
    long_description = readable.read()

setup(
    name="s2kindle",
    author="Antonio Feregrino",
    author_email="antonio.feregrino@gmail.com",
    version=VERSION,
    packages=packages,
    description="Send web articles to your kindle!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fferegrino/send-to-kindle",
    install_requires=list_requirements(requirements),
    tests_require=list_requirements(requirements_dev),
    entry_points="""
        [console_scripts]
        s2k=send_to_kindle.cli:download
    """,
    include_package_data=True,
    cmdclass={"verify": VerifyVersionCommand},
)
