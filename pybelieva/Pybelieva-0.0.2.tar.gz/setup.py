import setuptools

with open('README.rst', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='Pybelieva',
    version='0.0.2',
    description='Python wrapper for UnbelievaBoat API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/dev-cats/Pybelieva',
    author='Mr_ChAI & korochun',
    author_email='mr.kofe.edk@ya.ru',
    license='MIT',
    classifiers=[
        'Development Status :: 6 - Mature',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Communications :: Chat'
    ],
    keywords='UnbelievaBoat unbelievable pizza interface async aiohttp',
    project_urls={
        'Documentation': 'https://github.com/dev-cats/Pybelieva/wiki/Documentation',
        'Source': 'https://github.com/dev-cats/Pybelieva',
        'Tracker': 'https://github.com/dev-cats/Pybelieva/issues'
    },
    install_requires=['aiohttp'],
    packages=['unbelieva']
)
