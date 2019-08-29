from setuptools import setup


def readme():
	with open('README.md') as f:
		README = f.read()
	return README


setup(
	name="djangohome",
	version="1.0.1",
	license="MIT",
	description="Djangohome: Django Reusable app to design Home Page.",
	long_description=readme(),
	long_description_content_type="text/markdown",
	url="https://github.com/bhojrampawar/djangohome",
	author="Bhojram pawar",
	author_email="bhojrampawar@hotmail.com",
	packages=["djangohome"],
	include_package_data=True,
	classifiers=[
		'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
	],
	install_requires=['Django', 'djangorestframework', 'Pillow', 'djangorestframework_simplejwt'],
)

