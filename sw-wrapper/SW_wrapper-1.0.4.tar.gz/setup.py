from distutils.core import Extension, setup

libssw = Extension('libssw',
                   include_dirs=['sw_wrapper/'],
                   sources=['sw_wrapper/ssw.c'])  # ,
# extra_compile_args=['-Wall','-O3','-pipe','-fPIC','-shared','-rdynamic','-o'])
setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='SW_wrapper',
    url='https://github.com/AndreaTirelli1991/Complete-Striped-Smith-Waterman-Library',
    author='Andrea Tirelli',
    author_email='andrea.tirelli@ieo.it',
    # Needed to actually package something
    packages=['sw_wrapper'],
    ext_modules=[libssw],
    download_url='https://github.com/AndreaTirelli1991/Complete-Striped-Smith-Waterman-Library/archive/v_1.0.4.tar.gz',
    classifiers=[
        'Development Status :: 3 - Alpha', 'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3'],
    # *strongly* suggested for sharing
    version='1.0.4',
    package_data={'sw_wrapper': ['*.h']},
    headers=['sw_wrapper/ssw.h'],
    # The license can be anything you like
    license='MIT',
    description='A simple python wrapper for a C implementation of Smith-Waterman algorithm',

    # We will also need a readme eventually (there will be a warning)
    # long_description=open('README.txt').read(),
)
