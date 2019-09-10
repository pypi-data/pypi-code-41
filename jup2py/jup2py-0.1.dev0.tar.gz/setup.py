from setuptools import setup, find_packages
import codecs
import jup2py

with codecs.open("README.md", "r", "utf-8")as fh:
    long_description = fh.read()

setup(name='jup2py',
      version=str(jup2py.__version__),
      description='Convert jupyter notebook to .py file',
      long_description_content_type="text/markdown",
      long_description=long_description,
      url='https://github.com/shivam-kotwalia/jup2py',
      # Refer to https://pypi.org/classifiers/
      classifiers=[
          "Programming Language :: Python :: 3.6",
          "Development Status :: 1 - Planning",
          "Operating System :: OS Independent",
          "License :: OSI Approved :: MIT License",
      ],
      keywords='Convert jupyter notebook to .py',
      author='Shivam Kotwalia',
      author_email='shivamkotwalia@gmail.com',
      license='MIT License',
      install_requires=["nbconvert==5.5.0"],
      python_requires=">3.6,!=3.3.*",
      # packages=['jup2py'],
      packages=find_packages(exclude=("tests", "docs", "static")),
      zip_safe=False,
      entry_points={
          'console_scripts': ['jup2py = jup2py:run_main'],
      },
      include_package_data=True,
      )
