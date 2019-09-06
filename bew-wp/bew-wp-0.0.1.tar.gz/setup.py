import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()#.decode('utf-8','ignore')

setuptools.setup(
    name="bew-wp",
    version="0.0.1",
    author="Jinhang",
    author_email="jinhang.d.zhu@gmail.com",
    description="A very easy tool to publish Markdown post to your WordPress website",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JinhangZhu/bew",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)