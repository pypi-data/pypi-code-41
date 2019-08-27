import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="workspace-puller",
    version="0.0.22",
    author="onpositive",
    author_email="vasily@onpositive.com",
    description="Workspace build tool.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VasiliyLysokobylko/workspace-puller",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=['workspace', 'pull', 'puller'],
    entry_points={'console_scripts': ['workspace-puller = workspace_puller.main:start']},
    include_package_data=True,
    install_requires=[
        'certifi',
        'pyyaml',
        'urllib3 >= 1.21.1, < 1.25',
        'requests',
        'pydrive',
        'pyTelegramBotAPI',
        'file-downloader',
        'gitpython'
    ]
)
