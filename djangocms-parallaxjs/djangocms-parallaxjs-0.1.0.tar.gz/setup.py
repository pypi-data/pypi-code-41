from setuptools import setup, find_packages


setup(
    name="djangocms-parallaxjs",
    version="0.1.0",
    url='https://github.com/georgema1982/djangocms-parallaxjs',
    license='MIT',
    description="A Django CMS plugin that creates parallax effects",
    long_description=open('README.md').read(),
    author='George Ma',
    author_email='george.ma1982@gmail.com',
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
        'django-cms>=3.3.0',
    ],
    include_package_data=True,
    zip_safe=False,
)