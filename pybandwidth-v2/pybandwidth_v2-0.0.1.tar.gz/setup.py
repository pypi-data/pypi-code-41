import setuptools

setuptools.setup(
  name='pybandwidth_v2',
  packages=setuptools.find_packages(),
  version='0.0.1',
  license='MIT',
  description='Bandwidth API for v2 messaging',
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
