from setuptools import setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

setup(name='auto_emailer',
      version='1.0.1',
      description='auto-emailer library for Python',
      long_description=readme,
      long_description_content_type='text/x-rst',
      author='Adam Stueckrath',
      author_email='stueckrath.adam@gmail.com',
      url='https://github.com/adamstueckrath/auto-emailer',
      packages=['auto_emailer'],
      install_requires=['six>=1.9.0'],
      tests_require=['six>=1.9.0'],
      keywords='smtp email',
      license='MIT',
      classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            "Development Status :: 3 - Alpha",

            # Indicate who your project is intended for
            "Intended Audience :: Developers",
            'Topic :: Software Development :: Libraries :: Python Modules',

            # Pick your license as you wish (should match "license" above)
            'License :: OSI Approved :: MIT License',

            # Specify the Python versions you support here.
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7"]
      )
