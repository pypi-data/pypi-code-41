import setuptools

with open("README.md", "r",encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='ddm_robot',
    version='0.0.1',
    description='This is a packege for ddm_robot',
    author='Bob He',
    author_email='fastbiubiu@163.com',
    url='https://github.com/NocoldBob/robot',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
