from setuptools import setup, find_packages
from os import path


current_dir = path.abspath(path.dirname(__file__))
with open(path.join(current_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(name='gaplearn',
      version='0.11',
      description='Bridging gaps between other machine learning and deep learning tools and making robust, post-mortem analysis possible.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/awhedon/gaplearn',
      author='Alexander Whedon',
      author_email='alexander.whedon@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires = [
          'pandas',
          'numpy',
          'sklearn',
          'eli5'
      ],
      zip_safe=False)