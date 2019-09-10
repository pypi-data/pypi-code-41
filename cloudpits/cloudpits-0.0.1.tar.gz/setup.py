import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cloudpits",
    version="0.0.1",
    author="Caian Benedicto",
    author_email="caian@ggaunicamp.com",
    description="An AWS spot orchestrator for SPITZ enabled programs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hpg-cepetro/CloudPITS",
    packages=setuptools.find_packages(),
    scripts=[
        "bin/cloudpits_create_ondemand_jm",
        "bin/cloudpits_simulation",
        "bin/cloudpits_to_execute",
    ],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.6',
    install_requires=[
        "boto3",
        "pymysql"
    ],
)
