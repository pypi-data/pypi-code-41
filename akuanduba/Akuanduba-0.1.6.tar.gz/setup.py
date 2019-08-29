import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
  name = 'Akuanduba',
  version = '0.1.6',
  license='GPL-3.0',
  description = 'Akuanduba is a Python framework that eases manipulation of multiple running threads and shared resources. Its name was inspired by a god of the Brazilian mythology: Akuanduba, the god of order.',
  long_description = long_description,
  long_description_content_type="text/markdown",
  packages=setuptools.find_packages(),
  author = 'Gabriel Gazola Milan',
  author_email = 'gabriel.gazola@poli.ufrj.br',
  url = 'https://github.com/gabriel-milan/Akuanduba',
  keywords = ['framework', 'threading', 'shared resources', 'flexibility', 'python'],
  install_requires=[
          'datetime',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)