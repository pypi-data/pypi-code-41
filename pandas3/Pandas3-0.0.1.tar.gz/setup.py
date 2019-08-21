from setuptools import setup, find_packages

setup(
    name='Pandas3',
    version='v0.0.1',
    packages=find_packages(),
    url='',
    license='http://www.apache.org/licenses/LICENSE-2.0',
    author='Spencer Porter',
    author_email='spencer.porter3@gmail.com',
    description=' Boto3 extension to help facilitate data science workflows with S3 and Pandas',
    install_requires=['requests', 'boto3', 'pandas'],
    keywords=['aws', 's3', 'pandas', 'boto3']
)
