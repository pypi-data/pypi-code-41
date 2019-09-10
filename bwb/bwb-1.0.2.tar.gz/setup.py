import setuptools

setuptools.setup(name='bwb',
    version="1.0.2",
    description='bwb',
    long_description='bwb',
    author='bwb',
    license='QPL.txt',
    url='https://qotmail.com',
    packages=setuptools.find_packages(),
    install_requires=['base58', 'pycryptodome', 'pyotp'],
)
