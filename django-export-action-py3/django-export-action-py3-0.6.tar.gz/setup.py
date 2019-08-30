import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-export-action-py3",
    version="0.6",
    author="Juan José Garcia",
    author_email="juanjose.garciabeza@hotmail.com",
    description="Generic export action for Django's Admin for Python 3.6 and Django 2.x",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/juanjosegb/django-export-action_py3",
    packages=[
        'export_action',
    ],
    include_package_data=True,
    install_requires=['openpyxl'],
    license="MIT",
    zip_safe=False,
    keywords='django-export-action-py3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)

