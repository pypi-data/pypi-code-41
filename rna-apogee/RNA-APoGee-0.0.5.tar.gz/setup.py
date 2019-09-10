import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="RNA-APoGee",
    version="0.0.5",
    author="Sofia Panagiotopoulou",
    author_email="spanagiotopoulou@gillumina.com",
    description="A package for aligning RNA-seq data without reference biases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.illumina.com/spanag/APoGee",
    packages=['apogee'],
    install_requires=[
        'numpy>=1.16.4',
        'pandas>=0.25.1',
        'pyfasta>=0.5.2',
        'pysam>=0.15.2',
        'PyVCF>=0.6.8'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={'console_scripts': ['apogee=apogee.apogee_main:main',
                                      'create_genomes=apogee.create_genomes:main']},
)
