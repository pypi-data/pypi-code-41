from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.readlines()

long_description = "Utility to update dependencies in flutter project's pubspec.yaml"

setup(
    name='pubupd',
    version='1.0.4',
    author='Vineet Kumar',
    author_email='v1n@outlook.com',
    url='https://github.com/v1nvn/pubupd',
    description='Update pubspec.yaml',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pubupd=PubUpdater.pubupd:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords='flutter pub dart v1nvn',
    install_requires=requirements,
    zip_safe=False
)
