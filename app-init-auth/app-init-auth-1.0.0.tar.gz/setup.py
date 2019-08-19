from setuptools import setup, find_packages

setup(name = "app-init-auth",
   version = "1.0.0",
   description = "Authentication for webplatform",
   author = "Matthew Owens",
   author_email = "mowens@redhat.com",
   url = "https://github.com/app-init/auth",
   packages = find_packages(),
   include_package_data = True,
   install_requires = [
      "app-init-cli",
      "app-init-backend",
      'xmlsec',
      'python3_saml',
   ],
   dependency_links = [
      'http://github.com/lost-osiris/python3-saml/tarball/master#egg=python3_saml',
   ],
   python_requires='>=3',
   license='MIT',
   long_description = """TODO""",
   classifiers = [
       "Programming Language :: Python :: 3",
       "License :: OSI Approved :: MIT License",
       "Operating System :: OS Independent",
   ],
   # scripts = [
   #    "webplatform_auth/webplatform-auth"
   # ]
   entry_points={
       "console_scripts": ["webplatform-auth=webplatform_auth.cli:main"]
   },
   zip_safe = False
)
