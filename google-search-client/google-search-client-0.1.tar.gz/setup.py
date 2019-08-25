from setuptools import setup, find_packages

setup(
    name='google-search-client',
    version='0.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'requests',
        'beautifulsoup4',
        'lxml',
    ],
    url='https://github.com/justoy/google-search-client',
    license='MIT',
    author='justoy',
    author_email='li.justoy@gmail.com',
    description='A python client to scrape google search results',
)
