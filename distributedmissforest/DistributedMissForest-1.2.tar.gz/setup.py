from setuptools import setup

with open('README.md', 'r') as file:
  long_description = file.read()

setup(
  name = 'DistributedMissForest', 
  packages = ['DistributedMissForest'], 
  version = '1.02', 
  license='MIT', 
  description = 'MissForest in Python easy for Distribution on clusters', 
  author = 'Fangzhou Li', 
  author_email = 'fzli0805@gmail.com', 
  url = 'https://github.com/fangzhouli/DistributedMissForest', 
  download_url = 'https://github.com/fangzhouli/DistributedMissForest/archive/v_01.tar.gz', 
  keywords = ['imputation', 'cluster computing'], 
  install_requires=[            # I get to this in a second
          'numpy',
          'sklearn',
      ],
  long_description = long_description,
  long_description_content_type = 'text/markdown',
  classifiers=[
    'Development Status :: 3 - Alpha', 
    'Intended Audience :: Developers', 
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License', 
    'Programming Language :: Python :: 3', 
  ],
)