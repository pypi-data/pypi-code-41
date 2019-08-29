from setuptools import setup, find_packages


setup(
    name='acs_student_mail_harvester',
    version='1.0.1',
    url='https://github.com/petarmaric/acs_student_mail_harvester',
    license='BSD',
    author='Petar Maric',
    author_email='petarmaric@uns.ac.rs',
    description='Console app and Python API for harvesting email addresses of '\
                'our ACS students',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Education',
        'Topic :: Utilities',
    ],
    platforms='any',
    py_modules=['acs_student_mail_harvester'],
    entry_points={
        'console_scripts': ['acs_student_mail_harvester=acs_student_mail_harvester:main']
    },
    install_requires=open('requirements.txt').read().splitlines(),
)
