from setuptools import setup


install_requires = {
    'requests >= 2.22.0, < 2.23.0',
    'beautifulsoup4 >= 4.7.1, < 4.7.2',
    'flake8 >= 3.7.7, < 3.8.0',
    'pytest >= 5.0.0, < 5.1.0',
    'yamllint >= 1.16.0, < 1.17.0'
}


setup(name='commandict',
      version='0.1.0',
      description='Use Daum dic via CLI',
      url='http://github.com/nellag/commandict',
      author='nellaG',
      author_email='seirios0107@gmail.com',
      license='MIT',
      packages=['commandict'],
      entry_points='''
        [console_scripts]
        cmdct = commandict.get_result:main
        cmd = commandict.get_result:main
      ''',
      install_requires=list(install_requires),
      zip_safe=False)
