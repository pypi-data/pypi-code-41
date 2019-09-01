from setuptools import setup, find_packages
import distutils

class LocalesCommand(distutils.cmd.Command):
    description='compile locale files'
    def run(self):
        command = ["make" "update-langs"]
        subprocess.check_call(command)

setup (
    name="offlate",
    version="0.4.0",
    packages=find_packages(exclude=['.guix-profile*']),
    python_requires = '>=3',
    install_requires=['polib', 'ruamel.yaml', 'python-dateutil', 'PyQt5', 'pygit2',
        'python-gitlab', 'translation-finder'],
    entry_points={
        'gui_scripts': [
            'offlate=offlate.ui.main:main',
        ]
    },

    package_data={'offlate': ['data.json', 'locales/*.qm', 'locales/*.ts', 'icon.png']},
    cmdclass={
        'locales': LocalesCommand,
    },

    author="Julien Lepiller",
    author_email="julien@lepiller.eu",
    description="Offline translation interface for online translation tools.",
    license="GPLv3+",
    keywords="translation",
    url="https://framagit.org/tyreunom/offlate",
    classifiers=[
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 3 - Alpha',

    # Indicate who your project is intended for
    'Intended Audience :: End Users/Desktop',
    'Topic :: Software Development :: Localization',

    # Pick your license as you wish (should match "license" above)
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 3',
],
)
