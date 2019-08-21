import sys
from setuptools import setup, find_packages

setup(
    name="merchise.lint",
    version="0.14",
    description="Merchise Lint Checks (for CI)",
    long_description="Provide checkers to avoid common errors to check into your code.",
    classifiers=["Programming Language :: Python"],
    keywords="",
    author="Merchise Autrement",
    author_email="info@merchise.org",
    url="http://www.merchise.org/",
    license="GPL",
    packages=find_packages(exclude=["ez_setup"]),
    namespace_packages=["merchise"],
    include_package_data=True,
    zip_safe=False,
    install_requires=["flake8>=3.5,<3.8", "pycodestyle", "glob2>=0.4.1"],
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    entry_points={
        "console_scripts": [
            "merchise_lint = merchise.lint.main:main",
            "merchise_lint_pre_commit = merchise.lint.main:pre_commit",
            "merchise_lint%s = merchise.lint.main:main" % sys.version[:1],
            "merchise_lint_pre_commit%s = merchise.lint.main:pre_commit"
            % sys.version[:1],
        ],
        "flake8.extension": [
            "C901 = merchise.lint.checkers:AbsoluteImportCheck",
            "C980 = merchise.lint.checkers:AvoidPdb",
            "C990 = merchise.lint.checkers:BreakContinueCheck",
        ]
        + (
            ["O001 = merchise.lint.checkers:MangledI18NWithFStringsCheck"]
            if sys.version_info >= (3, 6)
            else []
        ),
    },
)
