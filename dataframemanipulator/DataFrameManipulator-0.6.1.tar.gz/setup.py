from distutils.core import setup

# PS3intGkXcEGKjw
# python setup.py sdist
# twine upload --skip-existing dist/*

SOURCE_CODE_DOWNLOAD_URL = 'https://github.com/NyAinaLorenzo/DataFrameManipulator/archive/v_0.6.1.zip'
VERSION = '0.6.1'

setup(
    name='DataFrameManipulator',  # How you named your package folder (MyLib)
    packages=['DataFrameManipulator'],  # Chose the same as "name"
    version=VERSION,  # Start with a small number and increase it with every change you make
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='Used on top of pandas',  # Give a short description about your library
    author='Lolo RAM',  # Type in your name
    author_email='lolo.ramaromanana@gmail.com',  # Type in your E-Mail
    url='https://github.com/NyAinaLorenzo/DataFrameManipulator',
    # Provide either the link to your github or to your website
    download_url=SOURCE_CODE_DOWNLOAD_URL,
    # I explain this later on
    keywords=['DATAFRAME', 'MANIPULATION'],  # Keywords that define your package best
    install_requires=[  # I get to this in a second
        'sklearn',
        'joblib',
        'numpy',
        'pandas',
        'requests',
        'boto3'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3',  # Specify which python versions that you want to support
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
