import setuptools

readme = ""

setuptools.setup(
    name='irpjs',
    version="0.0.2",
    author="Rasmus P J",
    author_email="wasmus@zom.bi",
    description="Server for the JavaScript LibreOffice Impress Remote.",
    url="https://rptr.github.io/gsoc/",
    packages=setuptools.find_packages(),
    install_requires=[
        "gevent-websocket"
    ],
)
