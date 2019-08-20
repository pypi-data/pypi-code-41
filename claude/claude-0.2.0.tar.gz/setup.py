from setuptools import setup, find_packages

setup(
    name = "claude",
    description = "Pluginable dashboard app",
    long_description = "Pluginable dashboard app",
    author = "Lajos Santa",
    author_email = "santa.lajos@gmail.com",
    url = "https://github.com/voidpp/claude",
    license = "MIT",
    use_scm_version = True,
    setup_requires = ["setuptools_scm"],
    install_requires = [
        "aiohttp~=3.5",
        "Jinja2~=2.10",
        "configpp~=0.3",
        "lxml~=4.4",
        "pymemcache~=2.2",
        "cssselect~=1.1",
        "cachetools~=3.1",
        "pychromecast~=3.2",
    ],
    include_package_data = True,
    packages = find_packages(),
    scripts = [
        "bin/start-claude-server"
    ],
    extras_require = {},
    classifiers = [],
)
