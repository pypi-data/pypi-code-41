from setuptools import setup


def read(fname):
    import os
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='luriegold',
      version='0.1.1',
      description=(
          "Lurie-Goldberg Algorithm to adjust a correlation "
          "matrix to be semipositive definite."),
      long_description=read('README.md'),
      long_description_content_type='text/markdown',
      url='http://github.com/kmedian/luriegold',
      author='Ulf Hamster',
      author_email='554c46@gmail.com',
      license='MIT',
      packages=['luriegold'],
      install_requires=[
          'setuptools>=40.0.0',
          'nose>=1.3.7',
          'numpy>=1.14.5',
          'scipy>=1.1.0',
          'scikit-learn>=0.19.2'],
      python_requires='>=3.6',
      zip_safe=False)
