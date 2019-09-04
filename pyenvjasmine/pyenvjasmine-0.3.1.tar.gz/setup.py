import os

from setuptools import setup

version = '0.3.1'

requires = [
    'coverage',
    'pyflakes',
    'pytest',
    'pytest-cov',
    'pytest-flakes',
]

def get_package_data(package, path):
    """
    Return a list of files to be added as package_data for the given path
    """
    data = []
    full_path = os.path.join(package, path)
    for root, dirs, files in os.walk(full_path):
        for f in files:
            data.append(os.path.join(root.replace(package+'/', ''), f))
    return data


setup(
    name='pyenvjasmine',
    version=version,
    description="A Python wrapper for envjasmine",
    long_description=open('README').read(),
    author='Sascha Welter',
    author_email='sw@betabug-sirius.ch',
    maintainer='Francisco de Borja Lopez Rio',
    maintainer_email='borja@codigo23.net',
    packages=['pyenvjasmine'],
    package_data = {
        'pyenvjasmine': get_package_data('pyenvjasmine', 'envjasmine') + \
        ['runner.html', 'runner3.html', 'run-jasmine3.js']
        },
    url='https://code.codigo23.net/trac/wiki/pyenvjasmine',
    download_url='http://pypi.python.org/pypi/pyenvjasmine#downloads',
    license='BSD licence, see LICENSE',
    install_requires=requires,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: JavaScript',
        'Topic :: Software Development',
        'Topic :: Software Development :: Testing',
        ]
)
