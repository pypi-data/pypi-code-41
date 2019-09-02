import pathlib
from setuptools import setup

setup(
    name="es_logging_machine",
    version="1.0.1",
    description="This library can be used to log data to your elasticsearch",
    long_description="This library can be used to log data to your elasticsearch",
    author="Shravan Naidu",
    author_email="shravan.jnaidu@yahoo.com",
    license="MIT",
    scripts=['es_logging_machine.py'],
    include_package_data=True,
    install_requires=["ConfigParser", "pytz", "datetime",
                      "elasticsearch", "certifi", "requests", "boto3"]
)
