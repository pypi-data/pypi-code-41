import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
        name="vapetool",
        version="1.0.1",
        author="Stanislaw Baranski",
        author_email="stachu@stasbar.com",
        description="VapeTool python utils",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/vape-tool/VapeTool-BatteriesParser",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            ],
        )
