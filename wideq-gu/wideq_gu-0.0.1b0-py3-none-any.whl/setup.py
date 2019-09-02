from setuptools import setup, find_packages


setup(
    name='wideq_gu',
    version='0.0.1a',
    description='LG SmartThinQ API client for Korean',
    author='gugu927',
    author_email='kimcg0927@gmail.com',
    url='https://github.com/gugu927/wideq',
    long_description=open('README.md').read(),
    license='MIT',
    platforms='ALL',
    install_requires=['requests'],
      packages=find_packages(exclude=['tests']),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)