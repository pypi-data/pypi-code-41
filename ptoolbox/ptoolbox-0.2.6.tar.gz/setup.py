from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

setup_args = dict(
    name='ptoolbox',
    version='0.2.6',
    description='Tools to work with multiple problem formats: DSA, Hackerrank, CMS, repl...',
    long_description_content_type="text/markdown",
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    packages=find_packages(exclude=('tests', )),
    author='Thuc Nguyen',
    author_email='gthuc.nguyen@gmail.com',
    keywords=['ptoolbox', 'problem tools'],
    url='https://gitlab.com/thucnguyen/ptoolbox',
    download_url='https://pypi.org/project/ptoolbox/',
    # py_modules=['firestoretools'],
    entry_points='''
        [console_scripts]
        ptoolbox=ptoolbox.ptoolbox:cli
    ''',
)

install_requires = [
    'click',
    'requests',
    'beautifulsoup4',
    'tomd',
    ''
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
