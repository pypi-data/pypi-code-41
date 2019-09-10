from setuptools import setup


setup(
    name='wideqlg',
    version='1.0.0',
    description='LG SmartThinQ API client',
    author='boralyl',
    url='https://github.com/boralyl/wideqlg',
    license='MIT',
    platforms='ALL',
    install_requires=['requests'],
    py_modules=['wideq'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
