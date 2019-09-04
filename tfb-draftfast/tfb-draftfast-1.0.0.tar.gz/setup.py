import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

requires = [
    'numpy==1.15.4',
    'terminaltables==3.1.0',
    'ortools==7.3.7083',
]

setuptools.setup(
    name='tfb-draftfast',
    version='1.0.0',
    author='Drew',
    author_email='drew@thefantasybros.com',
    description='A tool to automate and optimize DraftKings and FanDuel '
                'lineup construction.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/drew-tfb/tfb-draftfast',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=requires,
)
