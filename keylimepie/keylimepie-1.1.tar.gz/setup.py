from setuptools import setup



setup(
    name='keylimepie',
    version='v1.1',
    packages=['keylimepie', 'keylimepie.model', 'keylimepie.analysis'],
    scripts=['scripts/makeheader.py'],
    package_data={
        '':['*.c', '*.dat'],
    },
    url='https://gitlab.com/SmirnGreg/limepy/tree/python3',
    license='MIT',
    author='Richard Teague, Grigorii V. Smirnov-Pinchukov',
    author_email='smirnov@mpia.de',
    install_requires=[
        'numpy>=1.10',
        'astropy>=2.0',
        'scipy>=1.0',
    ],
    python_requires='>=3.6',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    description='Python tools to run and analyse LIME models'
)
