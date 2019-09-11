import io
import setuptools

with io.open('README.md', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(name='bwb',
    version='2.0.1',
    description='bwb',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='bwb',
    author_email='bwbpy@qotmail.com',
    license='QPL.txt',
    url='https://qotmail.com',
    packages=setuptools.find_packages(),
    install_requires=['base58', 'cryptography'],
)
