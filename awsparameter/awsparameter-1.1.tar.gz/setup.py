from setuptools import setup, find_packages

setup(
    name             = 'awsparameter',
    version          = '1.01',
    description      = 'use parameter in S3 with kms',
    author           = 'Nakyungwon',
    author_email     = 'saecomaster@gmail.com',
    # url              = 'https://github.com/rampart81/pyquibase',
    url              = 'https://github.com/Nakyungwon/parameter_s3_kms',
    # download_url     = 'https://githur.com/rampart81/pyquibase/archive/1.0.tar.gz',
    install_requires = [ 'boto3' ],
    packages         = find_packages(exclude = ['docs', 'tests*']),
    keywords         = ['s3', 'kms', 'ssm parameter'],
    python_requires  = '>=3',
    zip_safe=False,
    classifiers      = [
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ]
)