import setuptools

setuptools.setup(
    name='ghost-ts',
    version="1.2.1",
    author="admin",
    author_email='admin@shyouxia.cn',
    license='MIT',
    url='http://www.shyouxia.cn',
    description='A framework for developing Quantitative Trading programmes',
    long_description=__doc__,
    keywords='quant quantitative investment trading algotrading',
    classifiers=["Operating System :: OS Independent",
                 'Programming Language :: Python :: 3',
                 # 'Programming Language :: Python :: 3.6',
                 'Topic :: Office/Business :: Financial :: Investment',
                 'Programming Language :: Python :: Implementation :: CPython',
                 'License :: OSI Approved :: MIT License'],
    packages=setuptools.find_packages(),
)
