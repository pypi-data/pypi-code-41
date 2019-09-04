from distutils.core import setup

setup(
  name = 'filmykeeda',
  packages = ['filmykeeda','filmykeeda.utils','filmykeeda.modelDescriptions'],
  version = '0.1',
  license='MIT',
  description = 'A movie script generation library',
  author = 'Ashmeet Lamba',
  author_email = 'ashmeet.l13@gmail.com',
  url = 'https://github.com/ashmeet13/FilmyKeeda',
  download_url = 'https://github.com/ashmeet13/FilmyKeeda/archive/v0.1.2.tar.gz',
  keywords = ['NLP','GENERATION','GPT2','ULMFiT','OpenAI','Fast.ai'],
  install_requires=['rouge',
          'gpt_2_simple',
          'sentencepiece',
          'fastai',
          'pandas',
          'requests',
          'beautifulsoup4',
          'atlas',
          'tensorflow'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Topic :: Software Development :: Build Tools',    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
  ]
)