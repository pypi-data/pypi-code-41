import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gpt2",
    version="0.0.3",
    author="Open Medical IO",
    author_email="info@openmedical.io",
    description="API client for GPT-2 text generator cloud hosted by Open Medical IO",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/open-medical-io/cloud-gpt-2",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
