import setuptools

def readme():
    try:
        with open('README.md') as f:
            return f.read()
    except IOError:
        return ''
    
setuptools.setup(
    name="Quiik",
    version="1.6.2",
    author="Max Bridgland",
    install_requires=[
        'fabulous>=0.3.0'
    ],
    author_email="mabridgland@protonmail.com",
    description="Fun reaction based game in the terminal. Play full screen for best results!",
    long_description=readme(),
    long_description_content_type="text/markdown",
    entry_points = {
        'console_scripts': [
            'quiik = quiik.__main__:start'
        ]
    },
    keywords="command line, game, fun, terminal, object oriented",
    url="https://github.com/M4cs/Quiik",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Multimedia :: Graphics",
        "Operating System :: OS Independent"
    ),
)
