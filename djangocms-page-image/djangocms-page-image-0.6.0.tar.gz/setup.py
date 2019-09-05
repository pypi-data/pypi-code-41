from setuptools import setup, find_packages

from djangocms_page_image import __version__

setup(
    name="djangocms-page-image",
    version=__version__,
    url='http://github.com/febsn/djangocms-page-image',
    license='MIT',
    description="django-cms page extension providing image and teaser text",
    long_description=open('README.rst').read(),
    author='Fabian Lehner',
    author_email='fl@makonis.net',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    install_requires=[
        "Django >= 1.11",
        "django-filer >= 1.2.0",

        "django-cms >= 3.5",
        "django-sekizai >= 0.4.2",
        "easy_thumbnails >= 1.0",
    ],
    include_package_data=True,
    zip_safe=False,
)
