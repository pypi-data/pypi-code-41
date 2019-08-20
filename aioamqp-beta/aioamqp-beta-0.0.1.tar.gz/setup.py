from setuptools import find_packages, setup

setup(
    name='aioamqp-beta',
    version='0.0.1',
    description="self-aioamqp version",
    url='',
    author='hacfox',
    author_email='zz.hacfox@gmail.com',
    packages=find_packages(exclude=[]),
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: Chinese (Simplified)',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=['pamqp'],
    zip_safe=False
)
