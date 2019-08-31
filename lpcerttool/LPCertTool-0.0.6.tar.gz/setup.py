import setuptools

path = "./Readme.txt"
with open(path, "r") as fh:
    long_description = fh.read()

# 版本号要增加，不然上传不成功
setuptools.setup(
    name = "LPCertTool",
    version = "0.0.6",
    author = "Ning.Liu",
    author_email = "ning.liu@linkplay.com",
    description = "Linkplay MSP Certificate Tool",
    long_description = long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/liuning0930",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
    install_requires=[
        "PyQt5",
        "XlsxWriter",
        "xlrd"
    ],
    entry_points={
              'console_scripts': [
                  'lpcerttool=LPCertLog.LPCertReportUI:main',
              ],
          },
)
