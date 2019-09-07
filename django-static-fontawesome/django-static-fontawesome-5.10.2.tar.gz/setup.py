import os
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), "r", encoding="utf-8") as fobj:
    long_description = fobj.read()

requires = [
    "django",
]

setup(
    name="django-static-fontawesome",
    version="5.10.2",
    description="Django application contain font-awesome static files",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="zencore",
    author_email="dobetter@zencore.cn",
    license="MIT",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords=['django-static-fontawesome'],
    packages=find_packages(".", exclude=["demo", "manage"]),
    requires=requires,
    install_requires=requires,
    zip_safe=False,
    include_package_data=True,
)
