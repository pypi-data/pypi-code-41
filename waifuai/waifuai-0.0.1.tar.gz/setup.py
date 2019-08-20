from setuptools import setup, find_packages

setup(name='waifuai',
    version='0.0.1',
    author='WaifuAI',
    author_email='waifuai@users.noreply.github.com',
    url='https://github.com/waifuai',
    license='Apache 2.0',
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        'console_scripts': ['waifuai=waifuai:main'],
    },
)
