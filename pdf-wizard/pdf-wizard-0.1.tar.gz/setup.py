import setuptools

setuptools.setup(
    name="pdf-wizard",
    version="0.1",
    url="https://gitlab.com/saavedra29/pdf-wizard",
    description="A command line tool to list and tidy up pdf files",
    author="Aristeidis Tomaras",
    author_email="arisgold29@gmail.com",
    license="MIT",
    scripts=["pdfwizard/pdfwizard"],
    packages=["pdfwizard", "pdfwizard.models"],
    install_requires=["python-magic", "PyPDF4"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: Utilities"
    ],
    keywords="pdf command",
    zip_safe=False
)