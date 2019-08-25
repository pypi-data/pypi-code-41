import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='cryptools',
    version='0.0.1',
    author='adbforlife',
    author_email='adbforlife2018@gmail.com',
    description='easy-to-use implementations for ciphers, hashes, prngs, and attacks',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/adbforlife/cryptools.git',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
)

