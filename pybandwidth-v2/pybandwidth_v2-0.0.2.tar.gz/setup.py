import setuptools

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
  name='pybandwidth_v2',
  packages=setuptools.find_packages(),
  version='0.0.2',
  license='MIT',
  description='Bandwidth API for v2 messaging',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author='Reef Technologies',
  author_email='anuj.agarwal@reef.pl',
  url='https://github.com/reef-technologies/pybandwidth_v2',
  download_url='https://github.com/reef-technologies/pybandwidth_v2/archive/v_001.tar.gz',
  keywords=['python', 'bandwidth', 'v2', 'api', 'client'],   # Keywords that define your package best
  install_requires=[
      'requests',
  ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of package
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
  python_requires='>=3.6',
  project_urls={
    'Source': 'https://github.com/reef-technologies/pybandwidth_v2',
    'Tracker': 'https://github.com/reef-technologies/pybandwidth_v2/issues',
  },
)
