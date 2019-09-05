import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="linuk",
    version="1.0.0",
    author="Kazi_jaber",
    author_email="jaforjaber@gmail.com",
    description="Library to make coding easier",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Psychewolf/linuk",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
