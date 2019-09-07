# -*- coding: utf-8 -*-
import sys
import os
from setuptools import setup, Extension
from setuptools import find_packages

#########
# settings
#########

project_var_name = "wrapclib"
versionPython = "%s.%s" % (sys.version_info.major, sys.version_info.minor)
path = "Lib/site-packages/" + project_var_name
readme = 'README.rst'
history = "HISTORY.rst"
requirements = None

KEYWORDS = project_var_name + ', Xavier Dupré'
DESCRIPTION = """Python Wrapper for some C libraries."""
CLASSIFIERS = [
    'Programming Language :: Python :: 3',
    'Intended Audience :: Developers',
    'Topic :: Scientific/Engineering',
    'Topic :: Education',
    'License :: OSI Approved :: MIT License',
    'Development Status :: 5 - Production/Stable'
]


#######
# data
#######

# re2
sources_re2 = [
    'gitsrc/re2/bitstate.cc',
    'gitsrc/re2/compile.cc',
    'gitsrc/re2/dfa.cc',
    'gitsrc/re2/filtered_re2.cc',
    'gitsrc/re2/mimics_pcre.cc',
    'gitsrc/re2/nfa.cc',
    'gitsrc/re2/onepass.cc',
    'gitsrc/re2/parse.cc',
    'gitsrc/re2/perl_groups.cc',
    'gitsrc/re2/prefilter.cc',
    'gitsrc/re2/prefilter_tree.cc',
    'gitsrc/re2/prog.cc',
    'gitsrc/re2/re2.cc',
    'gitsrc/re2/regexp.cc',
    'gitsrc/re2/set.cc',
    'gitsrc/re2/simplify.cc',
    'gitsrc/re2/stringpiece.cc',
    'gitsrc/re2/tostring.cc',
    'gitsrc/re2/unicode_casefold.cc',
    'gitsrc/re2/unicode_groups.cc',
    'gitsrc/util/rune.cc',
    'gitsrc/util/strutil.cc',
    '_re2.cc',
]

packages = find_packages('src', exclude='src')
package_dir = {k: "src/" + k.replace(".", "/") for k in packages}
package_data = {
    project_var_name + ".js": ["*.js", "*.css"],
    project_var_name + ".re2": sources_re2,
}

############
# functions
############


def ask_help():
    return "--help" in sys.argv or "--help-commands" in sys.argv


def is_local():
    file = os.path.abspath(__file__).replace("\\", "/").lower()
    if "/temp/" in file and "pip-" in file:
        return False
    from pyquickhelper.pycode.setup_helper import available_commands_list
    return available_commands_list(sys.argv)


def verbose():
    print("---------------------------------")
    print("package_dir =", package_dir)
    print("packages    =", packages)
    print("package_data=", package_data)
    print("current     =", os.path.abspath(os.getcwd()))
    print("---------------------------------")

##########
# version
##########


if is_local() and not ask_help():
    def write_version():
        from pyquickhelper.pycode import write_version_for_setup
        return write_version_for_setup(__file__)

    write_version()

    versiontxt = os.path.join(os.path.dirname(__file__), "version.txt")
    if os.path.exists(versiontxt):
        with open(versiontxt, "r") as f:
            lines = f.readlines()
        subversion = "." + lines[0].strip("\r\n ")
        if subversion == ".0":
            raise Exception("Git version is wrong: '{0}'.".format(subversion))
    else:
        raise FileNotFoundError(versiontxt)
else:
    # when the module is installed, no commit number is displayed
    subversion = ""

if "upload" in sys.argv and not subversion and not ask_help():
    # avoid uploading with a wrong subversion number
    raise Exception(
        "Git version is empty, cannot upload, is_local()={0}".format(is_local()))

##############
# submodule
##############
# git submodule add -b master https://github.com/google/re2.git src/wrapclib/re2/gitsrc

##############
# common part
##############

if os.path.exists(readme):
    with open(readme, "r", encoding='utf-8-sig') as f:
        long_description = f.read()
else:
    long_description = ""
if os.path.exists(history):
    with open(history, "r", encoding='utf-8-sig') as f:
        long_description += f.read()

if "--verbose" in sys.argv:
    verbose()

if is_local():
    import pyquickhelper
    logging_function = pyquickhelper.get_fLOG()
    logging_function(OutputPrint=True)
    must_build, run_build_ext = pyquickhelper.get_insetup_functions()

    if must_build():
        out = run_build_ext(__file__)
        print(out)

    if "build_sphinx" in sys.argv and not sys.platform.startswith("win"):
        # There is an issue with matplotlib and notebook gallery on linux
        # _tkinter.TclError: no display name and no $DISPLAY environment variable
        import matplotlib
        matplotlib.use('agg')

    from pyquickhelper.pycode import process_standard_options_for_setup
    r = process_standard_options_for_setup(
        sys.argv, __file__, project_var_name,
        unittest_modules=["pyquickhelper"],
        additional_notebook_path=["pyquickhelper", "jyquickhelper"],
        additional_local_path=["pyquickhelper", "jyquickhelper"],
        requirements=["pyquickhelper", "jyquickhelper", "pybind11"],
        layout=["html"], github_owner='sdpython',
        add_htmlhelp=sys.platform.startswith("win"),
        coverage_options=dict(omit=["*exclude*.py"]),
        fexclude=lambda name: 'gitsrc' in name,
        fLOG=logging_function, covtoken=("c6f1a6de-be91-4d6e-9123-c9f144edae8d", "'_UT_37_std' in outfile"))
    if not r and not ({"bdist_msi", "sdist",
                       "bdist_wheel", "publish", "publish_doc", "register",
                       "upload_docs", "bdist_wininst", "build_ext"} & set(sys.argv)):
        raise Exception("unable to interpret command line: " + str(sys.argv))
else:
    r = False

if ask_help():
    from pyquickhelper.pycode import process_standard_options_for_setup_help
    process_standard_options_for_setup_help(sys.argv)

if not r:
    if len(sys.argv) in (1, 2) and sys.argv[-1] in ("--help-commands",):
        from pyquickhelper.pycode import process_standard_options_for_setup_help
        process_standard_options_for_setup_help(sys.argv)
    from pyquickhelper.pycode import clean_readme
    from wrapclib import __version__ as sversion
    long_description = clean_readme(long_description)
    root = os.path.abspath(os.path.dirname(__file__))

    if sys.platform.startswith("win"):
        libraries_re2 = ['kernel32']
        extra_compile_args_re2 = None
    elif sys.platform.startswith("darwin"):
        libraries_re2 = None
        extra_compile_args_re2 = ['-lpthread', '-stdlib=libc++', '-std=c++11',
                                  '-mmacosx-version-min=10.7']
    else:
        libraries_re2 = None
        extra_compile_args_re2 = ['-lpthread', '-std=c++11']

    ext_re2 = Extension('wrapclib.re2._re2',
                        [os.path.join(root, 'src/wrapclib/re2', name)
                         for name in sources_re2],
                        extra_compile_args=extra_compile_args_re2,
                        include_dirs=[os.path.join(
                            root, 'src/wrapclib/re2/gitsrc')],
                        libraries=libraries_re2)

    setup(
        name=project_var_name,
        ext_modules=[ext_re2],
        version='%s%s' % (sversion, subversion),
        author='Xavier Dupré',
        author_email='xavier.dupre@gmail.com',
        license="MIT",
        url="http://www.xavierdupre.fr/app/wrapclib/helpsphinx/index.html",
        download_url="https://github.com/sdpython/wrapclib/",
        description=DESCRIPTION,
        long_description=long_description,
        keywords=KEYWORDS,
        classifiers=CLASSIFIERS,
        packages=packages,
        package_dir=package_dir,
        package_data=package_data,
        setup_requires=["pyquickhelper", "pybind11"],
        install_requires=["pybind11"],
    )
