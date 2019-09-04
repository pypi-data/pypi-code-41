from setuptools import setup, find_packages


# def readme():
#     with open('README.rst') as f:
#         return f.read()


setup(name='karantools',
      version='0.1.8',
      description="Karan's useful Python utilities.",
      keywords='tools utils utilities toolkit',
      url='http://github.com/karan1149/karantools',
      author='Karan Singhal',
      author_email='karan1149@gmail.com',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False)
