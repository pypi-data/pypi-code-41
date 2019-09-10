from setuptools import setup, find_packages


requirements = []

setup(
      name="@projname@",
      version = "0.0.1", #@version@#
      description="handle,.in progressing..,APIs",
      author="@author@",
      url="https://github.com/@username@/@projname@",
      author_email='@email@', 
      license="MIT",
      long_description = "refer to .md files in https://github.com/@username@/@projname@",
      classifiers=[
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Programming Language :: Python',
          ],
      packages= find_packages(),
      entry_points={
          'console_scripts': [
              '@projname@=@projname@.bin:main'
          ]
      },
      package_data={
          'resources':['RESOURCES/*']
      },
      include_package_data=True,
      install_requires=requirements,
      py_modules=['@projname@'], 
)


# python3 setup.py bdist --formats=tar
# python3 setup.py sdist

