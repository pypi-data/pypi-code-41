from setuptools import setup, find_packages

setup_args = dict(
    name='marktest',
    version='1.0.3',
    description='Een test pippackage voor project',
    license='MIT',
    packages=find_packages(),
    author='Mark Rozing',
    author_email='markrozing@hotmail.nl',
    keywords=['test'],
)

if __name__ == '__main__':
    setup(**setup_args)