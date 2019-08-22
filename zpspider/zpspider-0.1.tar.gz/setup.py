from setuptools import setup, find_packages

setup(
    name='zpspider',
    version='0.1',
    url='http://www.monetware.com/',
    description='A high-level Web Crawling and Web Scraping framework',
    author='zengcd',
    author_email="author@example.com",
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': ['zpspider = monetSpider:execute']
    },
    classifiers=[
        'Framework :: Scrapy',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
    ],
    # python_requires='>=2.7',
    install_requires=[
        'pymongo==3.8.0',
        'xmltodict==0.12.0',
        'scrapy_redis==0.6.8',
        'setuptools==40.8.0',
        'Scrapy==1.7.3',
        'fake_useragent==0.1.11',
        'PyMySQL==0.9.3',
        'requests==2.21.0',
    ],
)
