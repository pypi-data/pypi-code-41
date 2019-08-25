import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cornea",
    version="1.0.0",
    author="Praveen Ravichandran",
    author_email="pravinba9495@gmail.com",
    description="A PyPI package to extract insightful information about an image using Machine Intelligence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pravinba9495/cornea",
    packages=setuptools.find_packages(),
    install_requires=["requests"],
    python_requires="~=3.7",
    license="MIT",
    keywords='python,image-classification,pip,pypi-package,cognitive-services,microsoft-azure,image-analysis'
)
