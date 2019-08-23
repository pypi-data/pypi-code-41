from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="rishiraj",
    version="1.0.0.2",
    description="A Python package to get weather reports for any location.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/wabrishi/rishiraj",
    author="Rishiraj",
    author_email="rishiraj.python@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["rishi_raj"],
    include_package_data=True,
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "rishiraj=rishi_raj.cli:main",
        ]
    },
)