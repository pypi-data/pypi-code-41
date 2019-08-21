import setuptools

with open("README.md", "r") as f:
    desc = f.read()

setuptools.setup(
    name="example_pkg_zzy",
    version='0.0.1',
    author='824zzy',
    author_email='zhuzhengyuan824@gmail.com',
    description='Template_package',
    long_desc = desc,
    long_desc_content_type='text/markdown',
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)