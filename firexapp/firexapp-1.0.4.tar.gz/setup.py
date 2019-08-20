from setuptools import setup, find_packages
import versioneer


setup(name='firexapp',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Core firex application libraries',
      url='https://github.com/FireXStuff/firexapp',
      author='Core FireX Team',
      author_email='firex-dev@gmail.com',
      license='BSD-3-Clause',
      packages=find_packages(),
      zip_safe=True,
      install_requires=[
          "distlib",
          "firexkit",
          "tqdm<=4.29.1",
          "xmlrunner",
          "redis==2.10.5",
          "celery[redis]==4.2.1",
          "kombu==4.2.1",           # app.inspect.active seems to be returning None all the time for Kombu==4.6.4
          "psutil",
          "python-Levenshtein"
      ],
      classifiers=[
          "Programming Language :: Python :: 3",
          "Operating System :: OS Independent",
          "License :: OSI Approved :: BSD License",
      ],
      entry_points={
          'console_scripts': ['firexapp = firexapp.application:main',
                              'flow_tests = firexapp.testing.test_infra:default_main',
                              'firex_shutdown = firexapp.submit.shutdown:main',
                              ]
      },
      )
