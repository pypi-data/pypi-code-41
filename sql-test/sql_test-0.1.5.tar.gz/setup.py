import os
import site
from setuptools import setup, find_packages

# Check for existing installation
update = False
package_path = site.getsitepackages()[1]
sql_test_path = package_path + '/sql_test'
if os.path.exists(sql_test_path):
    update = True
    print('Securing configuration files.')
    move_files = ['sql_config.py', 'sql_secrets.py']
    temp_dir = sql_test_path + '/temp'
    os.mkdir(temp_dir)
    for file in move_files:
        os.rename(os.path.join(sql_test_path, file), os.path.join(temp_dir, file))

with open('sql_test/README.md', 'r') as fh:
    long_description = fh.read()

setup(name='sql_test',
      version='0.1.5',
      author='Rebecca Barnes',
      author_email='rebeccaebarnes@gmail.com',
      description='Conduct quality assurance testing on database tables',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/rebeccaebarnes/sql_analysis',
      python_requires='>=3.5',
      packages=find_packages(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Environment :: Console',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Scientific/Engineering :: Information Analysis'
          ],
      install_requires=[
          'SQLAlchemy',
          'pandas',
          'seaborn',
          'psycopg2',
          'cx-Oracle'
          ],
      zip_safe=False)

if update:
    for file in move_files:
        os.rename(os.path.join(temp_dir, file), os.path.join(sql_test_path, file))
    os.rmdir(temp_dir)
    print('Configuration files secured.')
