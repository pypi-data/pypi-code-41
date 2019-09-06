
import os, sys
here = (os.path.abspath(os.path.dirname(__file__)))
src = os.path.join(here, "src")
sys.path.append(src)

from setuptools import setup, find_packages

with open("README.md") as f:
    LONG_DESCRIPTION = f.read()
  
setup(
	name="stay",
	description="Simple, even Trivial Alternative to Yaml",
	license="MIT",
	url="https://github.com/amogorkon/stay",
	version="0.2.1.post1",
	author="Anselm Kiefner",
	author_email="stay-pypi@anselm.kiefner.de",
	python_requires=">3.5",
	keywords=["json", "yaml", "toml", "config", "simple", "alternative"],
	classifiers=[
	"Development Status :: 4 - Beta",
	"Intended Audience :: Developers",
	"Natural Language :: English",
	"License :: OSI Approved :: MIT License",
	"Operating System :: OS Independent",
	"Programming Language :: Python :: 3 :: Only",
	"Programming Language :: Python :: Implementation :: CPython",
	"Topic :: Text Processing :: Markup"],
    packages=find_packages(where="src"),
    package_dir={"": "src",},
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    zip_safe=False,
)
