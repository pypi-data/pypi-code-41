from distutils.core import setup
setup(
    name = 'Py1337x',
    packages = ['Py1337x'],
    version = '0.2',
    license='MIT',
    description = 'Py1337x is a library which allows you to access and search 1337x.to. It also help you to sort the torrents by time, size, seeders and leechers and there are a lot more. ',
    author = 'Harshana',
    author_email = 'harshanamails@gmail.com',
    url = 'https://github.com/harshanas',
    download_url = 'https://github.com/harshanas/Py1337x/archive/0.1.tar.gz',
    keywords = ['1337x.to', 'torrent', 'torrent-search', 'torrent-sort', 'torrents'],
    install_requires=[
        'requests',
        'beautifulsoup4',
        ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        ],
    )
