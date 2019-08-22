from setuptools import setup


def read(fname):
    import os
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='pctl_scale',
      version='0.1.1',
      description=(
          "Scale a variable into an open interval (0,1) whereas values "
          "within a given lower and upper percentile maintain a linear "
          "relation, and outlier saturate towards the interval limits."
      ),
      long_description=read('README.md'),
      long_description_content_type='text/markdown',
      url='http://github.com/kmedian/pctl_scale',
      author='Ulf Hamster',
      author_email='554c46@gmail.com',
      license='MIT',
      packages=['pctl_scale'],
      install_requires=[
          'setuptools>=40.0.0',
          'scikit-learn>=0.19.2',
          'numpy>=1.14.5'],
      python_requires='>=3.6',
      zip_safe=False)
