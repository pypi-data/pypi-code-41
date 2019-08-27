import io
import re
import setuptools

with open("README.rst", "rt", encoding='utf8') as fh:
    long_description = fh.read()

install_requires= []
with open('requirements.txt', 'rt', encoding='utf8') as fh:
    for l in fh:
        install_requires.append(l.strip())

with io.open('pygamebg.py', 'rt', encoding='utf8') as f:
    src = f.read()
m = re.search(r'\_\_version\_\_\s*=\s*\"([^"]*)\"', src)
version = m.group(1)

setuptools.setup(
    python_requires=">=3",
    name="PygameBg",
    version=version,
    author="Fondacija Petlja",
    author_email="team@petlja.org",
    description="Pygame Toolbox for Beginners by Petlja",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/Petlja/PygameBg",
    install_requires=install_requires,
    include_package_data=False,
    zip_safe=True,
    py_modules = ["pygamebg"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)
