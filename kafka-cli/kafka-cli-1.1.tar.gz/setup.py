from setuptools import setup

setup(
    name = 'kafka-cli',
    version = '1.1', 
    description = ' Kafka CLI utility tool.',
    author = 'jack chen',
    author_email = 'chenwumail@foxmail.com',
    url = 'https://github.com/chenwumail/kafka-cli',
    packages = ['kafka_cli'],
    install_requires=[
        'kafka'
    ],
    entry_points = {
        'console_scripts': [
            'kafka-cli=kafka_cli.__main__:main'
        ]
    }
)
