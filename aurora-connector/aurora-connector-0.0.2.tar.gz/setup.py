import setuptools

with open("README.md", "r") as file:
    long_description = file.read()

requires = [
    "boto3 >= 1.9.215",
    "python-dateutil"
]

packages = [
    "aurora_connector",
    "aurora_connector.helpers"
]

setuptools.setup(
    name="aurora-connector",
    version="0.0.2",
    author="Alistair O'Brien",
    author_email="alistair@duneroot.co.uk",
    description="A Python AWS Aurora Serverless Connector.",
    long_description=long_description,
    include_package_data=True,
    long_description_content_type="text/markdown",
    url="https://github.com/johnyob/Aurora-Connector",
    packages=packages,
    install_requires=requires,
)
