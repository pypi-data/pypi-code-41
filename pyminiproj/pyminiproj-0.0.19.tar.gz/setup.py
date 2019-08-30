from setuptools import setup, find_packages

requirements = [
    'efdir'
]


setup(
      name="pyminiproj",
      version = "0.0.19", #@version@#
      description="creat a python project template DIR , includes some shell-scripts for git and pypi",
      author="dli",
      url="https://github.com/ihgazni2/pyminiproj",
      author_email='ihgazni2010@hotmail.com', 
      license="MIT",
      long_description = "refer to .md files in https://github.com/ihgazni2/pyminiproj",
      entry_points = {
         'console_scripts': ['pyminiproj=pyminiproj.bin:main']
      },
      package_data = {
          'template':["pyminiproj/proj-tem.zip"],
          'resources':["REOURCES/*"]
      },
      #import pkg_resources
      #pkg_resources.resource_filename("pyminiproj","@PROJNAME@")
      #/root/.cache/Python-Eggs/pyminiproj-0.1-py3.6.egg-tmp/pyminiproj/@PROJNAME@
      include_package_data=True,
      install_requires=requirements,
      classifiers=[
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Programming Language :: Python',
          ],
      packages= find_packages(),
      py_modules=['pyminiproj'], 
      )


# python3 setup.py bdist --formats=tar
# python3 setup.py sdist



















