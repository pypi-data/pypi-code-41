from setuptools import setup, find_packages

try:
    with open("README.rst", 'r') as fp:
        long_description = fp.read()
except IOError:
    print("Could not read README.rst, long_description will be empty.")
    long_description = ""

setup(
    name='lesana',
    version='0.3.0',
    packages=find_packages(),
    scripts=['scripts/lesana'],

    package_data={
        '': ['*.yaml']
        },
    test_suite='tests',

    install_requires=[
        # 'xapian >= 1.4',
        'ruamel.yaml',
        'jinja2',
        ],
    python_requires='>=3',

    # Metadata
    author="Elena ``of Valhalla'' Grandi",
    author_email='valhalla@trueelena.org',
    description='Manage collection inventories throught yaml files.',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    license='GPLv3+',
    keywords='collection inventory',
    url='https://lesana.trueelena.org/lesana',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        ],
    project_urls={
        'Source': 'https://git.trueelena.org/cgit.cgi/software/lesana/',
        'Documentation': 'https://git.trueelena.org/cgit.cgi/software/lesana/tree/docs',
        }
)
