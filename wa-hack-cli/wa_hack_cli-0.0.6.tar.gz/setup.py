from setuptools import setup

setup(name='wa_hack_cli',
    version='0.0.6',
    description='Client Library for the WhatsApp hack server.',
    url='https://foo.bar',
    author='grindsa',
    author_email='grindelsack@gmail.com',
    license='GPL',
    packages=['wa_hack_cli'],
    platforms='any',
    install_requires=[
        'threading',
    ],
    data_files=[('examples', ['examples/simple_cli.py', 'examples/simple_receive.py', 'examples/simple_sender.py'])],
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: German',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],    
    zip_safe=False,
    test_suite="test")