from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
        name = 'incenp.binseqs',
        version = '0.2.1',
        description = 'Support for binary sequence formats in Biopython',
        long_description = long_description,
        long_description_content_type = 'text/markdown',
        author = 'Damien Goutte-Gattat',
        author_email = 'dgouttegattat@incenp.org',
        url = 'https://git.incenp.org/damien/binseqs',
        classifiers = [
            'Development Status :: 1 - Planning',
            'Environment :: Console',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Topic :: Scientific/Engineering :: Bio-Informatics'
        ],
        install_requires = [
            'biopython'
        ],
        packages = [
            'incenp',
            'incenp.bio',
            'incenp.bio.seqio'
        ]
)
