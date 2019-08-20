import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='espapp_pkg',
      version='0.5.5',
      description='ESP applicaion',
      author='Karan',
      author_email='karan.rathore@viriminfotech.com',
      license='Virim',
      url = "https://github.com/emb-karan/espapp-pkg",
      packages=setuptools.find_packages(),
      package_dir={'espapp-pkg': 'espapp'},
      package_data={'espapp': ['data/*']},
      include_package_data=True,
      platforms='any',
      python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
      install_requires=[
          'uuid',
          'python-crontab',
          'requests',
      ],
      entry_points={
        'console_scripts': [
            'espapp=espapp.esp:main',
        ],
       },
      )
      
