from setuptools import setup

setup(name='poly_pack',
      version='0.23',
      description='Some helpful functions for polymer stuff',
      url='https://github.com/reha54321/poly_pack',
      author='Reha Mathur',
      author_email='reha_mathur@horacemann.org',
      license='MIT',
      packages=['poly_pack'],
      install_requires=[
          'matplotlib',
          'numpy',
          'scipy',
          'pyFAI',
          'fabio',
          'tifffile',
      ],
      include_package_data=True,
      zip_safe=False)
