import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="LocToWeatherAPI",
    version="0.0.2",
    author="Kinjal Das",
    author_email="kinjal.das86@gmail.com",
    description="Package for Generating weather data from place name and/or date",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KinjalDas/Location_To_Climate_API",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
