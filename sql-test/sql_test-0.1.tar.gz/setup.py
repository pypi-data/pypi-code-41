from setuptools import setup, find_packages

with open('sql_test/README.md', 'r') as fh:
    long_description = fh.read()

setup(name='sql_test',
      version='0.1',
      author='Rebecca Barnes',
      author_email='rebeccaebarnes@gmail.com',
      description='Conduct quality assurance testing on database tables',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/rebeccaebarnes/sql_analysis',
      packages=find_packages(),
      classifiers=[
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'License :: OSI Approved :: MIT License'
          ],
      zip_safe=False)
