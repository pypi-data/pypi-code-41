#! /usr/bin/env python


from setuptools import setup
setup(
    name='mdx-custom-span-class',
    version='1.1.3',
    author='Konrad Wasowicz',
    author_email='exaroth@gmail.com',
    description='Markdown extension which allows inserting span elements with custom class',
    url='https://github.com/wilhelmer/mdx_custom_span_class',
    py_modules=['custom-span-class'],
    install_requires=['Markdown>=2.0',],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup :: HTML'
    ]
)
