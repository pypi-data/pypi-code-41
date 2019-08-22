from setuptools import setup, find_packages

setup(name='manolyaconfig',
      version='0.2',
      description='The simplest config reader in the world',
      long_description='It reads your confs.ini file and read - list your sections and return your section info'
                       'as dictionary.',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='simplest config reader',
      url='https://github.com/kuttamuwa/PythonHandy/tree/master/configs',
      author='Umut Ucok',
      author_email='ucok.umut@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'markdown',
      ],
      include_package_data=True,
      zip_safe=False)
