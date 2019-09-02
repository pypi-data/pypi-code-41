import setuptools

with open("README.md","r") as fh:
    long_description = fh.read()

setuptools.setup(
        name='nickstoolbox',
        version='0.1',
        # scripts=['nickstoolbox'],
        author="Nicolas Shu",
        author_email="nicolas.s.shu@gmail.com",
        description="Package for useful frequent functions",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/nicolasshu/nickstoolbox",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
     ],
     python_requires='>=3.3',
 )

