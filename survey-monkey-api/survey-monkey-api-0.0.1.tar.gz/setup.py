import setuptools

with open("README.md", "r") as file:
    long_description = file.read()

requires = [
    "requests"
]

packages = [
    "survey_monkey"
]

setuptools.setup(
    name="survey-monkey-api",
    version="0.0.1",
    author="Alistair O'Brien",
    author_email="alistair@duneroot.co.uk",
    description="A simple Python client for the Survey Monkey API (v3).",
    long_description=long_description,
    include_package_data=True,
    long_description_content_type="text/markdown",
    url="",
    packages=packages,
    install_requires=requires,
)