import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='cm_platform_library',
    version='0.0.4',
    author="Trent Murray",
    author_email="trent@cloudmicro.io",
    description="Handles our platform and authentication requests",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/cloudmicro/pypi/cm_platform_library",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'sqlalchemy',
        'cm_service_library',
        'psycopg2-binary',
        'databases[postgresql]',
    ]
)
