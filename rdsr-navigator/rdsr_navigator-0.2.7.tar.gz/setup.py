import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='rdsr_navigator',
    version='0.2.7',
    author='Robert Vorbau',
    author_email='robert.vorbau@sll.se',
    description='Package for extracting data from DICOM RDSR files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=r'https://bitbucket.org/robertvorbau_ks/rdsr_navigator/',
    packages=setuptools.find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=['pydicom', ],
    classifiers=[
        'Intended Audience :: Healthcare Industry',
        'Topic :: Scientific/Engineering :: Physics',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6'
)
