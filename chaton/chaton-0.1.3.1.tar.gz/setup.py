from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='chaton',
      version='0.1.3.1',
      description='A small chatbot for social robots',
      long_description=long_description,
      long_description_content_type="text/markdown",
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
      ],
      keywords='chatbot robot',
      url='https://bitbucket.org/minsujang/chaton/src/master/',
      author='Minsu Jang',
      author_email='minsu@etri.re.kr',
      license='GPL 3.0',
      packages=['chaton'],
      install_requires=[
          'lark-parser',
      ],
      include_package_data=True,
      zip_safe=False)
