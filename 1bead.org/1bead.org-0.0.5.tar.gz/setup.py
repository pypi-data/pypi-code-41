import setuptools


setuptools.setup(
    name='1bead.org',
    version='0.0.5',

    author='Max Zheng',
    author_email='maxzheng.os@gmail.com',

    description='Web application for 1bead.org',
    long_description=open('README.md').read(),

    url='https://github.com/maxzheng/1bead.org',

    install_requires=open('requirements.txt').read(),

    license='MIT',

    packages=['web', 'static'],
    include_package_data=True,

    python_requires='>=3.6',
    setup_requires=['setuptools-git', 'wheel'],

    entry_points={
       'console_scripts': [
           'web-app = web.cli:main',
       ],
    },

    # Standard classifiers at https://pypi.org/classifiers/
    classifiers=[
      'Development Status :: 5 - Production/Stable',

      'Intended Audience :: End Users/Desktop',
      'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Content Management System',

      'License :: OSI Approved :: MIT License',

      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.6',
    ],

    keywords='web appplication for 1bead.org to nurture the greatness of life',
)
