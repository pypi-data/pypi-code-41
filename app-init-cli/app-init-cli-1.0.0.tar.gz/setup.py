from setuptools import setup, find_packages

setup(name = "app-init-cli",
   version = "1.0.0",
   description = "CLI used for a webplatform",
   author = "Matthew Owens",
   author_email = "mowens@redhat.com",
   url = "https://github.com/app-init/cli",
   packages = find_packages(exclude=('db')),
   include_package_data = True,
   install_requires = [
      'docker',
      'pymongo',
      'docopt',
      'pytz',
      'twine',
   ],
   python_requires='>=3',
   license='MIT',
   entry_points={
       "console_scripts": ["webplatform-cli=webplatform_cli.cli:main"]
   },
   #scripts = ["webplatform_cli/webplatform-cli"],
   long_description = """TODO""",
   classifiers = [
       "Programming Language :: Python :: 3",
       "License :: OSI Approved :: MIT License",
       "Operating System :: OS Independent",
   ],
   zip_safe = False
)
