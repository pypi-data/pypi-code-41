from setuptools import setup


with open("README.rst", "r") as fh:
    long_description = fh.read()


setup(name="GISIC",
      version='1.29',
      description="Gaussian Inflection Spline Interpolation Continuum",
      author='Devin D. Whitten',
      author_email='dwhitten@nd.edu',
      long_description=long_description,
      license="ND",
      packages=['GISIC'],
      zip_safe=False
)
