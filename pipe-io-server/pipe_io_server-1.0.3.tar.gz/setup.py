from setuptools import setup

with open('README.md', 'r') as ifile:
    long_description = ifile.read()

setup(
    name='pipe_io_server',
    version='1.0.3',
    author='Kristóf Tóth',
    author_email='mrtoth@strongds.hu',
    description='A trivial to use IPC solution based on pipes and newlines',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://git.strongds.hu/mrtoth/pipe-io-server',
    packages=['pipe_io_server'],
    package_dir={'pipe_io_server': 'pipe_io_server'},
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX'
    ],
)
