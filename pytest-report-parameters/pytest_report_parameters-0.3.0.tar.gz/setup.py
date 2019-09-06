from setuptools import setup

with open("README.rst", "rb") as fp:
    LONG_DESCRIPTION = fp.read().decode("utf-8").strip()

setup(
    name="pytest_report_parameters",
    use_scm_version=True,
    url="https://gitlab.com/mkourim/pytest-report-parameters",
    description="pytest plugin for adding tests' parameters to junit report",
    long_description=LONG_DESCRIPTION,
    author="Martin Kourim",
    author_email="mkourim@redhat.com",
    license="MIT",
    py_modules=["pytest_report_parameters"],
    setup_requires=["setuptools_scm"],
    install_requires=["pytest>=2.4.2", "six"],
    entry_points={"pytest11": ["pytest_report_parameters = pytest_report_parameters"]},
    keywords=["polarion", "py.test", "pytest", "testing"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Pytest",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
    ],
    include_package_data=True,
)
