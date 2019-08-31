import os
import site
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install

def manage_custom_config(command_subclass):
    """Mange customized config files during update."""
    # Ref: https://blog.niteo.co/setuptools-run-custom-code-in-setup-py/
    orig_run = command_subclass.run

    def modified_run(self):
        update = False
        site_packages = site.getsitepackages()[1]
        sql_test_path = site_packages + '/sql_test'
        # Check if sql_test is installed and move config files if so
        if os.path.exists(sql_test_path):
            print('Securing configuration files.')
            temp_dir = site_packages + '/temp'
            if not os.path.exists(temp_dir):
                os.mkdir(temp_dir)
            move_files = ['sql_config.py', 'sql_secrets.py']
            for file in move_files:
                os.rename(os.path.join(sql_test_path, file),
                          os.path.join(temp_dir, file))
            update = True

        # Run the regular command_subclass
        orig_run(self)

        # Move files back after update
        if update:
            for file in move_files:
                os.rename(os.path.join(temp_dir, file),
                          os.path.join(sql_test_path, file))
            print('Configuration files secured.')

    command_subclass.run = modified_run
    return command_subclass

@manage_custom_config
class CustomDevelopCommand(develop):
    pass

@manage_custom_config
class CustomInstallCommand(install):
    pass

with open('sql_test/README.md', 'r') as fh:
    long_description = fh.read()

setup(name='sql_test',
      version='0.1.5.a',
      author='Rebecca Barnes',
      author_email='rebeccaebarnes@gmail.com',
      description='Conduct quality assurance testing on database tables',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/rebeccaebarnes/sql_analysis',
      python_requires='>=3.5',
      packages=find_packages(),
      cmdclass={
          'develop': CustomDevelopCommand,
          'install': CustomInstallCommand
      },
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
