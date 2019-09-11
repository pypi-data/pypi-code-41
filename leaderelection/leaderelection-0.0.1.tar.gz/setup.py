from distutils.core import setup
setup(
  name = 'leaderelection',
  packages = ['leaderelection'],
  version = '0.0.1',
  license='GPL3',
  description = 'Kubernetes leader election',
  author = 'Joel Damata',
  author_email = 'joel.damata94@gmail.com',
  url = 'https://github.com/jdamata',
  download_url = 'https://github.com/jdamata/k8s-leader-election-py/archive/0.0.1.tar.gz',
  keywords = ['Kubernetes', 'Controller', 'Leader', 'Election'],
  install_requires=[
          'kubernetes',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
  ],
)
