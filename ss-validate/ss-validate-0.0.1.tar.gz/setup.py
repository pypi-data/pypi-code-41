from setuptools import setup

setup(
    name='ss-validate',
    version='0.0.1',
    packages=['validate'],
    entry_points={
        "console_scripts": ['ss-validate = validate.validator:main']
    },
    url='https://github.com/EBISPOT/gwas-sumstats-validator',
    author='EBI SPOT',
    install_requires=['pandas_schema']
)
