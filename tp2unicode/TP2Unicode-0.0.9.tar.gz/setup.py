import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TP2Unicode",
    version="0.0.9",
    author="Tân, Khèng-iông",
    author_email="fernandochen799@gmail.com",
    description="共Taiwanese package拍出來的羅馬字轉做其他環境mā會當顯示的編碼",
    py_modules=['TP2Unicode/轉換器'],
    package_data={'TP2Unicode': ['data/*.csv']},
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/i3thuan5/Taiwanese-serif-to-Unicode",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
