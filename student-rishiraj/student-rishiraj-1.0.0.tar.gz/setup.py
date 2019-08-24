from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="student-rishiraj",
    version="1.0.0",
    description="A Python package to manage student details easy",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/wabrishi/student",
    author="Rishiraj",
    author_email="rishiraj.python@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["rishi_raj"],
    include_package_data=True,
    install_requires=["requests","mysql.connector","tkcalendar","tkinter"],
    entry_points={

    },
)