from setuptools import setup, find_packages

setup(
    name='decode-job',
    version='0.2.15',
    description='Base job structure to run jobs in the Limos',
    url='https://github.com.br/decodedata/decode-job',
    author='Decode',
    author_email='developer@decode.buzz',
    license='unlicense',
    packages=find_packages(),
    download_url="https://github.com/decodedata/decode-job/archive/0.2.15.tar.gz",
    install_requires=[
        'selenium', 'boto3', 'requests', 'proxy-requests', 'beautifulsoup4',
        "pdfminer.six"
    ],
    zip_safe=False)
