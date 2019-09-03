from setuptools import setup

setup(
    name='counter_r5_elasticsearch',
    version='0.4',
    packages=['counter_r5', 'counter_r5.tests'],
    install_requires=['elasticsearch', 'python-dateutil'],
    extras_require={  # Optional
        'test': ['pytest'],
    },
    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish
        'License :: OSI Approved :: GNU Affero General Public License v3',

        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='>=3.6,<4',
    package_data={'': ['schemas/elasticsearch_mapping.json']},
    url='',
    license='AGPL',
    author='Erudit',
    author_email='',
    description='Generate Counter R5 reports from an elasticsearch index'
)
