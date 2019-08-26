from setuptools import setup, find_packages

__VERSION__ = '2019.1a5'

setup(
    name='rscli',
    version=__VERSION__,
    description="Reckonsys CLI toolchain",  # NOQA
    long_description="CLI Toolchain",
    url='https://github.com/reckonsys/rscli',
    author='dhilipsiva',
    author_email='dhilipsiva@pm.me',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='rscli reckonsys cli toolchain',
    packages=find_packages(),
    install_requires=[
        'invoke', 'pick', 'requests'
    ],
    entry_points={
        'console_scripts': ['rscli = rscli.main:program.run']
    }
)
