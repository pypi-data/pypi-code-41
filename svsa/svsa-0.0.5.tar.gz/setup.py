import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='svsa',
      version='0.0.5',
      url='https://gjhunt.github.io/svsa/',
      author='Gregory J. Hunt',
      author_email='ghunt@wm.edu',
      description='Fast approximations of scattering spectra with SVR.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      license='GPL3',
      packages=setuptools.find_packages(),
      install_requires=[
          'pandas',
          'numpy',
          'scipy',
          'sklearn'
          ],
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
          "Operating System :: OS Independent",
          'Topic :: Scientific/Engineering',
      ],
    zip_safe=True)
