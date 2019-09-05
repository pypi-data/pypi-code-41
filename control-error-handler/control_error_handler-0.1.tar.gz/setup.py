from setuptools import setup, find_packages

with open('README.rst', 'r') as file:
    long_description = file.read()

setup(name='control_error_handler',
      version='0.1',
      description='Error handler for flask with sending exceptions to control service.',
      long_description=long_description,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.7',
          'Topic :: Text Processing :: Linguistic',
      ],
      keywords='flask, control service, exception, error_handler, 54origins',
      author='54origins',
      author_email='opensource@54origins.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'flask>=1.0',
          'requests>=2.22.0'
      ],
      include_package_data=True,
      python_requires='>=3.0, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.3.*, !=3.4.*, !=3.6.*',
      zip_safe=False)
