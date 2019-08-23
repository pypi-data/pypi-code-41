from setuptools import setup

import versioneer

with open("README.rst", "rb") as f:
    readme = f.read().decode("utf-8")

setup(
    name="photo-import",
    packages=["photoimport"],
    entry_points={
        "console_scripts": ['photo-import = photoimport.command:main']
    },
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Application to import photos into a hierarchical structure based on the EXIF data of the photos.",
    long_description=readme,
    long_description_content_type="text/x-rst",
    author="Edd Armitage",
    author_email="edward.armitage@gmail.com",
    url="https://gitlab.com/eddarmitage/photo-import",
    license="MIT",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='>=3.4',
    install_requires=["exif", "docopt"],
    setup_requires=[],
    tests_require=["pyfakefs", "nose2", "behave"],
    extras_require={
        'python_version<3.5': ['typing==3.7.4.1', ],
    },
)
