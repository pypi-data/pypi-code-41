from setuptools import setup, find_packages

setup(
    name='AutoTrackers',
    version='1.0.1',
    packages=find_packages(),
    url='https://github.com/zaw007/AutoTrackers',
    license='LGPL',
    author='zaw',
    author_email='zhangqishao007@foxmail.com',
    description='为 torrent 文件增加 Tracker 地址',
    long_description=open('README.md', 'r', encoding='utf8').read(),
    long_description_content_type="text/markdown",
    zip_safe=False
)
