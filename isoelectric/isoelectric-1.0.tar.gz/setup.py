import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="isoelectric",
    version="1.0",
    author="Lukasz Pawel Kozlowski",
    author_email="lukasz.kozlowski.lpk@gmail.com",
    description="IPC (Isoelectric Point Calculator) - prediction of isoelectric point of proteins and peptides",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://isoelectric.org",
    keywords = "protein, peptide, isoelectric point, pI, biochemistry, proteomics",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Public Domain",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
    include_package_data=True,
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.png', '*.faa'],
        'ipc': ['*.txt', '*.png', '*.faa'],
        'ipc/examples': ['*.txt', '*.png', '*.faa'],        
    },    
)

