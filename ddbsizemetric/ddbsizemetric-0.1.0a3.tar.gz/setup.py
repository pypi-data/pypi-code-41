import json
import setuptools

kwargs = json.loads("""
{
    "name": "ddbsizemetric",
    "version": "0.1.0-alpha.3",
    "description": "Lambda Custom Resource that emits a metric on the size of your DynamoDB Tables.",
    "url": "https://git-codecommit.us-east-1.amazonaws.com/v1/repos/ConstructRepo.git",
    "long_description_content_type": "text/markdown",
    "author": "Richard Boyd<Richard@rboyd.dev>",
    "project_urls": {
        "Source": "https://git-codecommit.us-east-1.amazonaws.com/v1/repos/ConstructRepo.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "ddbsizemetric",
        "ddbsizemetric._jsii"
    ],
    "package_data": {
        "ddbsizemetric._jsii": [
            "ddbsizemetric@0.1.0-alpha.3.jsii.tgz"
        ],
        "ddbsizemetric": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii~=0.15.1",
        "publication>=0.0.3",
        "aws-cdk.aws-events~=1.5,>=1.5.0",
        "aws-cdk.aws-events-targets~=1.5,>=1.5.0",
        "aws-cdk.aws-iam~=1.5,>=1.5.0",
        "aws-cdk.aws-lambda~=1.5,>=1.5.0",
        "aws-cdk.core~=1.5,>=1.5.0"
    ]
}
""")

with open('README.md') as fp:
    kwargs['long_description'] = fp.read()


setuptools.setup(**kwargs)
