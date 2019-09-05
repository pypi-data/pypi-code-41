from setuptools import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()


setup(
    name='pre-commit-pylint-wrapper-pythonpath',
    version='0.0.0',
    long_description=readme,
    py_modules = ['pre_commit_pylint_wrapper'],
    install_requires=['pylint==2.3.1'],
    python_requires=">=3.4",
    entry_points={
        "console_scripts": [
            "pre-commit-pylint-wrapper = pre_commit_pylint_wrapper:main"
        ]
    }
)
