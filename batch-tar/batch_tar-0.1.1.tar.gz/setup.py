import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="batch_tar",
    version="0.1.1",
    author='Guanliang Meng',
    author_email='linzhi2012@gmail.com',
    description="To tar/compress files/directories in batch mode.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3',
    url='https://github.com/linzhi2013/batch_tar',
    packages=setuptools.find_packages(),
    include_package_data=True,
    # install_requires=[],

    entry_points={
        'console_scripts': [
            'batch_tar=batch_tar.batch_tar:main',
        ],
    },
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
    ),
)