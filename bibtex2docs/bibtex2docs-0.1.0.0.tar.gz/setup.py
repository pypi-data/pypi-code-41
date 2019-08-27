from distutils.core import setup
LONG_DESCRIPTION = '''Translate BibTeX references from a Google Docs document'''

setup(
  name = 'bibtex2docs',
  scripts = ['bin/bibtex2docs.py'],
  install_requires=['nameparser',
                    'google-api-python-client',
                    'google-auth-httplib2',
                    'google-auth-oauthlib',
                    'bibtexparser'],
  version = '0.1.0.0',
  description = 'Translate BibTeX references from a Google Docs document',
  author = 'Greg Operto',
  long_description=LONG_DESCRIPTION,
  author_email = 'goperto@barcelonabeta.org',
  url = 'https://gitlab.com/xgrg/bibtex2docs',
  download_url = 'https://gitlab.com/xgrg/bibtex2docs/-/archive/0.1/bibtex2docs-0.1.tar.gz',
  classifiers = ['Intended Audience :: Science/Research',
      'Intended Audience :: Developers',
      'Topic :: Scientific/Engineering',
      'Operating System :: Unix',
      'Programming Language :: Python :: 3.7' ]
)
