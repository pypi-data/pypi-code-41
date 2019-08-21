from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='pyHooke',
      version='0.2.0',
      description='Open source plagiarism checker',
      long_description=readme(),
      long_description_content_type='text/markdown',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='plagiarism nlp plag scan levenshtein',
      url='http://github.com/oekshido/hooke',
      author='oekshido',
      author_email='oekshido@gmail.com',
      license='Apache-2.0',
      packages=['Hooke'],
      install_requires=[
          'fuzzysearch',
          'tika',
          'wget',
          'BeautifulSoup4',
          'nltk',
          'textract',
          'Google-Search-API'
      ],
      dependency_links=['https://github.com/abenassi/Google-Search-API/tarball/master', 'https://github.com/oekshido/textract/tarball/master'],
      include_package_data=True,
      zip_safe=False)
