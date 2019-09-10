import io
import setuptools

with io.open('README.md', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(name='bwb',
    version="1.0.3",
    description='bwb',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='bwb',
    author_email='bwbpy@qotmail.com',
    license='QPL.txt',
    url='https://qotmail.com',
    packages=setuptools.find_packages(),
    install_requires=['base58', 'pycryptodome', 'pyotp'],
)
