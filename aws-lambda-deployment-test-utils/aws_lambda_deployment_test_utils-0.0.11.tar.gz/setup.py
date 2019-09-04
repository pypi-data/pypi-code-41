#! /usr/bin/env python
import os

from setuptools import setup

PROJECT_ROOT, _ = os.path.split(__file__)
REVISION = "0.0.11"
PROJECT_NAME = "aws_lambda_deployment_test_utils"
PROJECT_AUTHORS = "Salim Fadhley"
PROJECT_EMAILS = "salimfadhley@ecs.co.uk"
PROJECT_URL = "https://bitbucket.org/salimfadhley_ecs/aws_lambda_deployment_test_utils/src/master/"
SHORT_DESCRIPTION = "Tools to simplify pre and post deployment testing of AWS Lambdas."

try:
    DESCRIPTION = open(os.path.join(PROJECT_ROOT, "README.md")).read()
except IOError:
    DESCRIPTION = SHORT_DESCRIPTION

try:
    REQUIREMENTS = list(open("requirements.txt").read().splitlines())
except IOError:
    REQUIREMENTS = []


try:
    DEV_REQUIREMENTS = list(open("dev_requirements.txt").read().splitlines())
except IOError:
    DEV_REQUIREMENTS = []

setup(
    name=PROJECT_NAME.lower(),
    version=REVISION,
    author=PROJECT_AUTHORS,
    author_email=PROJECT_EMAILS,
    packages=["lambda_deployment_test_utils"],
    zip_safe=True,
    include_package_data=False,
    install_requires=REQUIREMENTS,
    url=PROJECT_URL,
    description=SHORT_DESCRIPTION,
    long_description=DESCRIPTION,
    license="GPL4",
)
