import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="IndigoPy",
    version="0.0.1a2",
    author="Indigo Mad",
    author_email="indigomad@pku.edu.cn",
    description="Basic function is done",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IndigoMad/IndigoPy.git",
    packages=setuptools.find_packages(),
    data_files=[('Doc/examples', ['Doc/examples/newscreen.py']),
    ('Doc/Protein',['Doc/Protein/pdb.md']),
    ('Doc/Math',['Doc/Math/Funcmaker.md'])],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Unix"
    ],
    install_requires=[
          'numpy','scipy','matplotlib'
      ],
    python_requires='>=3'
)