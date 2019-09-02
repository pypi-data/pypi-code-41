from setuptools import setup


def readme():
    with open('README.rst', 'r') as f:
        return f.read()


setup(
    name='DelumoWave',
    version='0.1.20',
    description='API for Delumo radio controller',
    long_description=readme(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Topic :: Home Automation',
        'Topic :: System :: Hardware',
        'Topic :: System :: Hardware :: Hardware Drivers',
    ],
    license='MIT',
    author='Roman Alexeev',
    author_email='roman@alexeyev.su',
    url='https://bitbucket.org/delumo/DelumoWave',
    packages=['delumowave', 'delumowave.config'],
    install_requires=[
        'pyserial >= 3.4',
    ],
    include_package_data=True,
    zip_safe=False,
)
