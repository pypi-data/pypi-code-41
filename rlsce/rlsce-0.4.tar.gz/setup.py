from distutils.core import setup
setup(
    # How you named your package folder (MyLib)
    name='rlsce',
    packages=['rlsce'],   # Chose the same as "name"
    version='0.4',      # Start with a small number and increase it with every change you make
    # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    license='MIT',
    # Give a short description about your library
    description='Robo Laura Sentry Capture Exception',
    author='William R. Sanches',                   # Type in your name
    author_email='william.sanches@laura-br.com',      # Type in your E-Mail
    # Provide either the link to your github or to your website
    url='https://github.com/Wrsanches/rlsce',
    # I explain this later on
    download_url='https://github.com/Wrsanches/rlsce/archive/v0.4.tar.gz',
    # Keywords that define your package best
    keywords=['Robo', 'Laura', 'Sentry', 'Capture', 'Exception'],
    install_requires=[            # I get to this in a second
        'datetime',
        'sentry_sdk',
    ],
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
