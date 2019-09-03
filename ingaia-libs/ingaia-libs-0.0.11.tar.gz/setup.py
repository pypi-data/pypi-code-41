import os.path
from setuptools import setup

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

README = "See the README file"
# The text of the README file
with open(os.path.join(HERE, "Readme.md")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(
    name="ingaia-libs",
    version="0.0.11",
    description="inGaia Python Utility Library",
    long_description=README,
    long_description_content_type="text/markdown",
    url="http://gitlab.ingaia.com.br/operacoes/libs/ingaia-libs",
    author="inGaia Operations",
    author_email="suporte.operacoes@i-value.com.br",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    packages=["ingaia", "ingaia.constants", "ingaia.gcloud", "ingaia.request_logger"],
    include_package_data=False,
    install_requires=["google-cloud-firestore", "google-cloud-datastore", "google-cloud-tasks", "google-cloud-storage",
                      "google-cloud-bigquery", "flask", "google-cloud-scheduler", "werkzeug", "decorator", "requests"],
    entry_points={
        "console_scripts": [
            "ingaia-libs=ingaia.__main__:main",
        ]
    },
)
