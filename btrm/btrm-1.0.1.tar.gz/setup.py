from setuptools import setup, find_packages

setup(
    name='btrm',
    version='1.0.1',
    author='Linh Nguyen',
    author_email='linh1612340@gmail.com',
    url='https://github.com/nobabykill/btrm',
    description='Alternative tool for rm command in linux using python',
    platforms=['window', 'linux', 'macos'],
    keywords=['btrm', 'backup than remove'],
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'argparse',
    ],
    entry_points={
            'console_scripts': [
                'btrm = sources.btrm:main'
            ]},
    include_package_data=True,
)
