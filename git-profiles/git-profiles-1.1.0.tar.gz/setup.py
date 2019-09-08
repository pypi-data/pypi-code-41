# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

modules = \
['git_profiles']
entry_points = \
{'console_scripts': ['git-profiles = src:git_profiles']}

setup_kwargs = {
    'name': 'git-profiles',
    'version': '1.1.0',
    'description': 'Python package that helps you easily manage and switch between multiple git profiles.',
    'long_description': '<div align="center">\n    <h1 align="center">👥 git-profiles</h1>\n    <p align="center">Python package that helps you easily manage and switch between multiple git configurations</p>\n    <p align="center">\n        <a href="https://github.com/popadi/git-profiles">\n            <img src="https://travis-ci.com/popadi/git-profiles.svg?branch=master" alt="Build">\n            <img src="https://coveralls.io/repos/github/popadi/git-profiles/badge.svg?branch=master&service=github">\n            <img src="https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat-square" alt="Software License">\n        </a>\n    </p>\n</div>\n\n# About\nSoon\n\n# Install\nSoon\n\n# Usage\n```\nusage: git_profile.py [-h] [-f [PATH]] [-g] [-v] [-q]\n                      {list,current,destroy,add,use,del,update,show} ...\n\ngit-profiles usage:\n\npositional arguments:\n  {list,current,destroy,add,use,del,update,show}\n    list                List the current available profiles\n    current             Show the current active configuration for the current\n                        project. If the global parameter is specified, the\n                        global configuration will be returned instead\n    destroy             Deletes all the profiles created using this package\n    add                 Adds a new profile configuration with the given name.\n                        The userwill be prompted to input the username, the\n                        e-mail (required) and the signing key (optional).\n    use                 Set the given profile as the active one for the\n                        current project. If the global parameter is specified,\n                        the new profile will be set globally\n    del                 Delete the given profile from the configuration file\n    update              Update the details of the given profile name\n    show                Show the details of the given profile\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -f [PATH], --config-file [PATH]\n                        Specify a git config file. If no configuration file is\n                        given, the default=$HOME/.gitconfig will be used; if\n                        no configuration file is found, the command won\'t be\n                        executed\n  -g, --globally        Applies the other commands globally\n  -v, --version         show program\'s version number and exit\n  -q, --quiet           Executes the given command but disables the program\n                        output\n```\n\n# Examples\n\n### Adding a profile\n```\n$ git-profiles add work\nEnter the profile user: Adrian Pop\nEnter the profile mail: adrianpop@work.domain.com\nEnter the profile profile signing key: ABCD1234WXYZ\n\n[INFO] Successfully created profile work:\n\tName: Adrian Pop\n\tMail: adrianpop@work.domain.com\n\tSigning key: ABCD1234WXYZ\n```\n\n### Updating the details of a profile\n```\n$ git-profiles update work\nEnter the new user (Adrian Pop): Pop Adrian\nEnter the new mail (adrianpop@work.domain.com): work@domain.com\nEnter the new signing key (ABCD1234WXYZ): WXYZ1234ABCD\n\n[INFO] Successfully updated profile work\n\tName: Pop Adrian\n\tMail: work@domain.com\n\tSigning key: WXYZ1234ABCD\n```\n\n### Removing a profile\n```\n$ git-profiles del work-account\n[ERROR] Profile work-account was not found\n\n$ git-profiles del work\n[INFO] Successfully deleted profile work\n```\n\n### Listing the existing profiles\n```\n$ git-profiles list\nAvailable profiles:\n\tmain <-- active globally\n\twork\n\thome <-- active locally\n\ttest-profile\n```\n\n### Show details about a profile\n```\n$ git-profiles show work\nwork\n\tName: Adrian Pop\n\tMail: adrianpop@work.domain.com\n\tSigning key: ABCD1234WXYZ\n```\n\n### Using a profile\n```\n$ git-profiles -g use home\n[INFO] Switched to home globally\n\n$ git-profiles use work\n[INFO] Switched to work locally\n\n$ git-profiles list\nAvailable profiles:\n\tmain\n\twork <-- active locally\n\thome <-- active globally\n\ttest-profile\n```\n\n### Delete all the profiles\n```\n$ git-profiles destroy\n[INFO] Successfully deleted 4 profiles\n```\n\n# Credits\nThanks to Zeeshan Ahmad for inspiring me to write this package for python. You can check his equivalent package written in php [here](https://github.com/ziishaned/git-profiles).\n\n# License\nMIT © 2019 Pop Adrian\n',
    'author': 'Adrian Pop',
    'author_email': 'popadrian1996@gmail.com',
    'url': 'https://github.com/popadi/git-profiles',
    'package_dir': package_dir,
    'py_modules': modules,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
