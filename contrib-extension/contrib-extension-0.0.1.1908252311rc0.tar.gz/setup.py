from setuptools import setup, find_packages

setup(name='contrib-extension',
      version='v0.0.1.1908252311-rc',
      url='https://github.com/Sotaneum/contrib-extension',
      license='MIT',
      author='Donggun LEE',
      author_email='gnyotnu39@gmail.com',
      description='contrib-extension',
      packages=find_packages(exclude=['tests']),
      long_description=open('README.md', encoding='UTF8').read(),
      long_description_content_type='text/markdown',
      zip_safe=False,
      setup_requires=[],
      classifiers=[
          'License :: OSI Approved :: MIT License'
      ]
)
