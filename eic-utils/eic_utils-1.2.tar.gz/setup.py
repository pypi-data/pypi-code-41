import setuptools

with open("./README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='eic_utils',
      version='1.2',
      description='basic utils for python3',
      url='http://github.com/indestinee/utils',
      author='indestinee',
      author_email='indestinee@gmail.com',
      long_description=long_description,
      long_description_content_type="text/markdown",
      packages=setuptools.find_packages(),
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
