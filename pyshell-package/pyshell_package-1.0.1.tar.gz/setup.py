from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="pyshell_package",
    version="1.0.1",
    description="A rudimentary UNIX-like shell that allows extensibility using custom python modules to implement various features as shell commands.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://git.corp.adobe.com/priyanss/python-mini-project",
    author="Samridhi Chaubey",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=["python_mini_project", "python_mini_project/commands"],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "pyshell_package=python_mini_project.core_event:main",
        ]
    },
)