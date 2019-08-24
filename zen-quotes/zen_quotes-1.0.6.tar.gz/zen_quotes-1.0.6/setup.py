from setuptools import setup, find_packages

setup(
    name='zen_quotes',
    version_format="{tag}.dev{commitcount}",
    setup_requires=["setuptools-git-version"],
    packages = find_packages(),
    description='A sample lib Zen of Python',
    author='Yuri Mussi',
    author_email='ymussi@gmail.com',
    license='BSD',
    url='https://github.com/ymussi/zen_quotes',
    keywords = "Mussi",
    install_requires = ['requests'],
    zip_safe=False
    ),