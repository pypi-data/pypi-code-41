import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
      name='pyncaids',
      description='National Competent Authority (NCA) Identifiers as a Python module',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Jacek Artymiak',
      author_email='jacek@artymiak.com',
      url='https://github.com/badmetacoder/pyncaids',
      version='0.0.1',
      py_modules=['pyncaids.pyncaids'],
      packages=setuptools.find_packages(),
      classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
        "Natural Language :: English",
      ],
      python_requires='>=3.7',
)