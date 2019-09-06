from setuptools import setup

setup(
    name="ebv_helpers",
    version="1.0.9",
    author_email="yasinmeydan@gmail.com",
    description="helpers functions",
    url="https://github.com/yasinmeydan/ebv_helpers.git",
    packages=['ebv_helpers'],
    install_requires=['elasticsearch==6.0.0',
                      'pika>=1.0.1',
                      'requests>=2.22.0',
                      'pymongo>=3.4.0']
)
