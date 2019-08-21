
"""
Based on Tkinter, this module offers a class called "AskForColor" that
opens a window for the user to set a color in RGB system.
To get the value in format "#RRGGBB" (used on Tkinter as a pattern),
just use the "get( )" method.
A default color is needed. See the next example:
        from ask_for_color import AskForColor 
        ask = AskForColor("#1a2b3c")
        color = ask.get() # it returns a string color like "#rrggbb"
        numcolor = ask.getnum() # it returns a tuple of int like (12,34,56)

run the command or follow the url
git clone https://github.com/jeykun/AskForColor.git
"""
from setuptools import setup,find_packages
from codecs import open
from os import path
here = path.abspath(path.dirname(__file__))
try:
    with open(path.join(here,'DESCRIPTION.rst'), encoding='utf-8') as f:
        long_description = f.read()
except:
    long_description = ''


#ajuda em https://www.youtube.com/watch?v=Lb0b4ro0ze4&list=PLV7VqBqvsd_0u42lQtg4FU-rWeOSsbzOT&index=5
setup(
    # Ver PEP 426 (name)
    # Iniciar ou terminar com letra ou numero
    name='ask_for_color',
    # Ver PEP 440
    # O formato pode ser assim:
    # 1.2.0.dev1    Development release
    # 1.2.0a1       Alpha Release
    # 1.2.0b1       Beta Release
    # 1.2.0rc1      Release Candidate
    # 1.2.0         Final Release
    # 1.2.0.post1   Post Release
    # 15.10         Date based release
    # 23            Serial release
    version = '0.1.3',
    description = 'A GUI interface to get from the user a color string in RGB system.',
    #long_description = 'Using Tkinter module, it allows the user to set any color in RGB system like "#rrggbb".',
    url = 'https://github.com/jeykun/AskForColor.git',
    author = 'Junior R. Ribeiro',
    author_email = 'juniorribeiro2013@gmail.com',
    license = 'Free for non-commercial use',
    classifiers = [
        # How mature is this project? Common values are
        #   2   Alpha
        #   4   Beta
        #   5   Production/Stable
        'Development Status :: 5 - Production/Stable',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Artistic Software',
        # Pick your license as you wish (should match "license" above)
        'License :: Free for non-commercial use',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        ],
    keywords = ['GUI','Tkinter','RGB','color','Interface'],
    packages = find_packages(),
    install_requires = ['sh>=1.11'],
    data_files = []    
    )
