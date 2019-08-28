from setuptools import setup, find_packages

with open('README.md') as readme_file:
  README = readme_file.read()

with open('HISTORY.md') as history_file:
  HISTORY = history_file.read()

setup_args = dict(
  name='o4',
  version='0.1',
  description='Useful pipeline for detecting vehicles and pedestrians and extract features from the detcetion.',
  long_description_content_type="text/markdown",
  long_description=README + '\n\n' + HISTORY,
  license='MIT',
  packages=find_packages(),
  author='Miguel de Matos',
  author_email='miguelcarvalhaismatos@ua.pt',
  keywords=['Detection', 'Tracking', 'Fingerprint'],
  # url='https://github.com/ncthuc/elastictools',
  download_url='https://pypi.org/project/o4/'
)

install_requires = [
  'absl-py==0.7.1',
  'asn1crypto==0.24.0',
  'astor==0.7.1',
  'certifi==2019.6.16',
  'cffi==1.12.3',
  'chardet==3.0.4',
  'cryptography==2.7',
  'cycler==0.10.0',
  'gast==0.2.2',
  'grpcio==1.16.1',
  'h5py==2.8.0',
  'idna==2.8',
  'imutils==0.5.2',
  'Keras==2.2.2',
  'Keras-Applications==1.0.4',
  'Keras-Preprocessing==1.0.2',
  'kiwisolver==1.1.0',
  'Markdown==3.1.1',
  'matplotlib==3.1.0',
  'mkl-fft==1.0.12',
  'mkl-random==1.0.2',
  'munkres==1.1.2',
  'numpy==1.16.4',
  'olefile==0.46',
  'Pillow==6.0.0',
  'protobuf==3.6.0',
  'pycparser==2.19',
  'pyOpenSSL==19.0.0',
  'pyparsing==2.4.0',
  'PySocks==1.7.0',
  'python-dateutil==2.8.0',
  'pytz==2019.1',
  'PyYAML==5.1',
  'requests==2.22.0',
  'scipy==1.2.1',
  'six==1.12.0',
  'tensorboard==1.10.0',
  'tensorflow==1.10.0',
  'termcolor==1.1.0',
  'tornado==6.0.2',
  'urllib3==1.24.2',
  'Werkzeug==0.15.4',
  'win-inet-pton==1.1.0',
  'wincertstore==0.2',

]

if __name__ == '__main__':
  setup(**setup_args, install_requires=install_requires)
