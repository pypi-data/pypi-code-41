from setuptools import setup

setup(name='iats',
      version='0.0.2',
      description='minimal ats jupyter kernel',
      author='Richard K',
      author_email='qpotizo@gmail.com',
      license='MIT',
      classifiers=[
        'License :: OSI Approved :: MIT License',
      ],
      url='https://github.com/sparverius/iats/',
      download_url='https://api.github.com/repos/sparverius/iats/tarball/0.0.2',
      packages=['iats'],
      scripts=['iats/install_ats_kernel'],
      keywords=['ats', 'jupyter', 'notebook', 'kernel'],
      include_package_data=True
      )
