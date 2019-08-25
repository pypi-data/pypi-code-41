from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='zec2',
    version="0.3.0",

    description='Easily ssh to your AWS EC2 instances',
    long_description=readme(),
    long_description_content_type='text/markdown',

    url='https://github.com/arrrlo/zec2',
    licence='MIT',

    author='Ivan Arar',
    author_email='ivan.arar@gmail.com',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='amazon, aws, ec2, ssh, instance',

    packages=['zec2'],
    install_requires=[
        'click~=6.3',
        'six~=1.11.0',
        'boto3~=1.7.69',
        'terminaltables~=3.1.0'
    ],

    entry_points={
        'console_scripts': [
            'zec2=zec2.cli:cli'
        ],
    },

    project_urls={
        'Source': 'https://github.com/arrrlo/zec2',
    },
)
