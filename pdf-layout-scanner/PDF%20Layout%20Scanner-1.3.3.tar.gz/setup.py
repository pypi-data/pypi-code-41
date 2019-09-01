import setuptools

setuptools.setup(
    name='PDF Layout Scanner',
    version='1.3.3',
    packages=['pdf_layout_scanner'],
    license='MIT',
    author='Yoshihiko Ueno',
    url='https://github.com/yoshihikoueno/pdfminer-layout-scanner',
    author_email='windows7home@hotmail.co.jp',
    install_requires=['pandas', 'tqdm', 'pdfminer.six', ],
    long_description=open('./README.md').read(),
    long_description_content_type="text/markdown",
)
