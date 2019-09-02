import setuptools

def readme():
    with open('README.md') as f:
        return f.read()

setuptools.setup(
    name='card-trick',
    version='0.2.0',
    description='Utility package to find gene - drug relationships within CARD',
    long_description=readme(),
    long_description_content_type='text/markdown',
    author='Anthony Underwood',
    author_email='au3@sanger.ac.uk',
    license='MIT',
    packages=setuptools.find_packages(),
    scripts=['scripts/card-trick'],
    install_requires=['pronto', 'requests'],
    test_suite='nose.collector',
    tests_require=['nose'],
    include_package_data=True,
    package_data={'card_trick': ['data/*.json']},
    classifiers=[ 
        'Development Status :: 3 - Alpha', 
        'Intended Audience :: Science/Research', 
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ]
)
