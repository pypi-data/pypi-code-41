import setuptools

requirements = ['boto3', 'pyyaml']

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
      name='jmpr',
      version='0.1.1',
      author='eGT Labs',
      author_email='egtlabs@eglobaltech.com',
      description='Tooling to permit AWS account navigation',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/eGT-Labs/jmpr',
      license='MIT',
      packages=['jmpr'],
      entry_points = {
            'console_scripts': ['jmpr=jmpr.cli:main'],
      },
      install_requires=requirements,
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)