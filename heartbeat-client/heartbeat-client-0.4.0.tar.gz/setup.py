import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="heartbeat-client",
    version="0.4.0",
    author="Hawthorn2013",
    author_email="hawthorn7dd@hotmail.com",
    description="Heartbeat client implements with python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Hawthorn2013/heartbeat-client-python",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['heartbeat=heartbeat_client.main:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)