from setuptools import setup, find_packages

install_requires = []

setup(
    name='mkpyproject',
    version='0.0.1',
    description='Command line utility for initializing an empty Py package',
    url='https://github.com/jay-tyler/mkpyproject',
    author_email='jmtyler+dev@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(exclude=['docs', 'tests', 'scripts']),
    python_requires='>=3.7',
    install_requires=install_requires,
    
)
