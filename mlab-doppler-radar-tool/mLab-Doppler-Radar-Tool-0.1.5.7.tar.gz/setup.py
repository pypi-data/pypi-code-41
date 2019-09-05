from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(name='mLab-Doppler-Radar-Tool',
      version='0.1.5.7',
      packages=['mLab_DopplerRadar'],
      install_requires=[
          'pyserial','pyqtgraph'
      ],
      include_package_data=True,
      url='', license='MIT',
      author='Alex Kuan',
      author_email='agathakuannew@gmail.com',
      description='mLab Doppler Radar UART tool and example code',
      long_description=long_description,
      long_description_content_type='text/markdown')