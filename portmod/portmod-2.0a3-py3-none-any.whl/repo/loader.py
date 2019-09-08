# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from typing import Dict
import ast
import sys
import glob
import os
import traceback
import importlib
import copyreg
import re
from types import ModuleType
from RestrictedPython import (
    compile_restricted_exec,
    RestrictingNodeTransformer,
    safe_globals,
    limited_builtins,
)
from RestrictedPython.Guards import safer_getattr, guarded_iter_unpack_sequence
from RestrictedPython.Eval import default_guarded_getitem, default_guarded_getiter
from copy import deepcopy
from portmod.log import warn
from portmod.repo.atom import atom_sat
from portmod.globals import env
from portmod.repo.metadata import get_categories
from .atom import Atom
from ..pybuild_interface import Pybuild
from ..safemodules.io_guard import _check_call, IOType


# We store a cache of mods so that they are only loaded once
# when doing dependency resolution.
# Stores key-value pairs of the form (filename, Mod Object)
__mods: Dict[str, Pybuild] = {}

WRAPPED_IMPORTS = {"filecmp", "os", "sys", "shutil", "os.path"}
WHITELISTED_IMPORTS = {
    "portmod",
    "portmod.pybuild",
    "portmod.pybuild.modinfo",
    "portmod.safemodules",
    "re",
    "json",
    "typing",
    "fnmatch",
} | {"portmod.safemodules." + imp for imp in WRAPPED_IMPORTS}

ALLOWED_IMPORTS = WRAPPED_IMPORTS | WHITELISTED_IMPORTS


class SafeModule(ModuleType):
    def __init__(self, name, dictionary, cache=None):
        super().__init__(name)
        self.__dict__.clear()
        if cache is None:
            cache = {}
        for key in dictionary:
            if (
                not isinstance(dictionary[key], ModuleType)
                or ".".join([name, key]) in WHITELISTED_IMPORTS
            ):
                if isinstance(dictionary[key], type):
                    try:

                        class Derived(dictionary[key]):
                            pass

                        self.__dict__[key] = Derived
                    except TypeError:
                        # If we can't derive it, skip it entirely.
                        # The user probably doesn't need this type
                        pass
                elif isinstance(dictionary[key], ModuleType):
                    self.__dict__[key] = SafeModule(
                        dictionary[key].__name__, dictionary[key].__dict__, cache
                    )
                elif name in cache and key in cache[name]:
                    self.__dict__[key] = cache[name][key]
                else:
                    try:
                        self.__dict__[key] = deepcopy(dictionary[key])
                    except TypeError:
                        # If we fail to copy it, just ignore it.
                        # It's probably not going to be needed by the user.
                        # It may on the other hand be needed by the module during
                        # execution as we may execute on the Safe Module.
                        # My apologies for the inconvenience
                        pass
        cache[name] = self.__dict__


def reduce_mod(m):
    if m.__name__ not in WHITELISTED_IMPORTS:
        return None.__class__, ()
    return SafeModule, (m.__name__, m.__dict__)


copyreg.pickle(ModuleType, reduce_mod)
copyreg.pickle(SafeModule, reduce_mod)


def safe_import(_cache=None):
    cache = _cache or {}
    # We store a deepcopy module cache at the pybuild level. I.e. pybuilds are isolated
    # from each other, but we don't have to recursively clone every module they use
    clone_cache = {}

    def _import_root(name, glob=None, loc=None, fromlist=(), level=0):
        def _import(name, glob=None, loc=None, fromlist=(), level=0):
            """
            Safe implementation of __import__ to use with RestrictedPython
            """
            if glob:
                absolute_name = importlib.util.resolve_name(
                    level * "." + name, glob["__name__"]
                )
            else:
                absolute_name = importlib.util.resolve_name(level * "." + name, None)

            path = None
            if "." in absolute_name:
                parent_name, _, child_name = absolute_name.rpartition(".")
                parent_module = _import(parent_name)
                path = parent_module.__spec__.submodule_search_locations

            if absolute_name in cache:
                return cache[absolute_name]
            if absolute_name in WHITELISTED_IMPORTS or absolute_name.startswith(
                "pyclass"
            ):
                if absolute_name.startswith("pyclass"):
                    spec = safe_find_spec(absolute_name, path, cache)
                    spec.loader = RestrictedLoader(absolute_name, spec.origin)
                    spec.loader.cache = cache
                    module = importlib.util.module_from_spec(spec)
                    __SAFE_MODULES[absolute_name] = module
                else:
                    spec = importlib.util.find_spec(absolute_name, path)
                    spec.loader = importlib.machinery.SourceFileLoader(
                        absolute_name, spec.origin
                    )
                    module = importlib.util.module_from_spec(spec)
                if path is not None:
                    setattr(parent_module, child_name, module)
                cache[absolute_name] = module
                module.__loader__.exec_module(module)
                return module
            raise Exception(f"Unable to load restricted module {absolute_name}")

        module = _import(name, glob, loc, fromlist, level)
        if name.startswith("portmod.safemodules."):
            importname = (
                "portmod.safemodules."
                + name.split("portmod.safemodules.")[-1].split(".")[0]
            )
        else:
            importname = name.split(".")[0]

        importname = name.split(".")[0]
        toimport = SafeModule(importname, cache[importname].__dict__, clone_cache)
        for key in fromlist or []:
            setattr(toimport, key, getattr(module, key))
        return toimport

    return _import_root


# Default implementation to handle invalid pybuilds
class Mod:
    def __init__(self):
        raise Exception("Mod is not defined")


def _write_wrapper():
    # Construct the write wrapper class
    def _handler(secattr, error_msg):
        # Make a class method.
        def handler(self, *args):
            try:
                f = getattr(self.ob, secattr)
            except AttributeError:
                raise TypeError(error_msg)
            f(*args)

        return handler

    class Wrapper(object, metaclass=type):
        def __init__(self, ob):
            object.__getattribute__(self, "__dict__")["ob"] = ob

        __setitem__ = _handler(
            "__guarded_setitem__", "object does not support item or slice assignment"
        )

        __delitem__ = _handler(
            "__guarded_delitem__", "object does not support item or slice assignment"
        )

        __setattr__ = _handler(
            "__guarded_setattr__", "attribute-less object (assign or del)"
        )

        __delattr__ = _handler(
            "__guarded_delattr__", "attribute-less object (assign or del)"
        )

    return Wrapper


def write_guard():
    """
    Write guard that blocks modifications to modules
    """
    bannedtypes = {ModuleType}
    Wrapper = _write_wrapper()

    def guard(ob):
        if type(ob) in bannedtypes:
            return Wrapper(ob)
        else:
            return ob

    return guard


def safe_open(path, mode="r", *args, **kwargs):
    """
    Safe function for opening files that can be used by pybuilds
    """
    _check_call(path, IOType.Read)
    if "w" in mode or "+" in mode or "a" in mode or "x" in mode:
        _check_call(path, IOType.Write)

    if not re.match(r"[rwxabt\+]+", mode):
        raise Exception("Invalid mode string!")

    return open(path, mode, *args, **kwargs)


SAFE_GLOBALS = deepcopy(safe_globals)
SAFE_GLOBALS.update(
    {
        "Mod": Mod,
        "__metaclass__": type,
        "_getattr_": safer_getattr,
        "_getitem_": default_guarded_getitem,
        "_write_": write_guard(),
        "super": super,
        "_getiter_": default_guarded_getiter,
        "_iter_unpack_sequence_": guarded_iter_unpack_sequence,
    }
)


class PrintWrapper:
    def __init__(self, _getattr_=None):
        self.txt = []
        self._getattr_ = _getattr_

    def write(self, text):
        self.txt.append(text)

    def __call__(self):
        return "".join(self.txt)

    def _call_print(self, *objects, **kwargs):
        if kwargs.get("file", None) is None:
            kwargs["file"] = sys.stdout
        else:
            self._getattr_(kwargs["file"], "write")
        print(*objects, **kwargs)


SAFE_GLOBALS["__builtins__"].update(
    {"_print_": PrintWrapper, "open": safe_open, "set": set, "frozenset": frozenset}
)
SAFE_GLOBALS["__builtins__"].update(limited_builtins)


class Policy(RestrictingNodeTransformer):
    def visit_JoinedStr(self, node):
        return self.node_contents_visit(node)

    def visit_FormattedValue(self, node):
        return self.node_contents_visit(node)

    def visit_AnnAssign(self, node):
        return self.node_contents_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name in WRAPPED_IMPORTS:
                alias.asname = alias.asname or alias.name
                alias.name = "portmod.safemodules." + alias.name
        return RestrictingNodeTransformer.visit_Import(self, node)

    def visit_ImportFrom(self, node):
        if node.module in WRAPPED_IMPORTS:
            node.module = "portmod.safemodules." + node.module
        module = importlib.import_module(node.module)
        for name in node.names:
            if isinstance(module.__dict__.get(name.name), type(importlib)):
                self.error(node, "Importing modules from other modules is forbidden")

        if node.module == "portmod.pybuild.modinfo":
            del sys.modules[node.module]

        return RestrictingNodeTransformer.visit_ImportFrom(self, node)

    def visit_Name(self, node):
        if node.id == "super":
            self.error(node, "Use of name super not allowed")
        return RestrictingNodeTransformer.visit_Name(self, node)

    def visit_FunctionDef(self, node):
        node = RestrictingNodeTransformer.visit_FunctionDef(self, node)
        if node.name == "__init__":
            newnode = ast.parse("super().__init__()").body[0]
            newnode.lineno = node.lineno
            newnode.col_offset = node.col_offset
            node.body.insert(0, newnode)
        return node


class RestrictedLoader(importlib.machinery.SourceFileLoader):
    def create_module(self, spec):
        return None

    def exec_module(self, module):
        with open(module.__file__, "r") as module_file:
            tmp_globals = deepcopy(SAFE_GLOBALS)
            tmp_globals["__builtins__"]["__import__"] = safe_import(
                self.__dict__.get("cache", None)
            )
            tmp_globals.update(module.__dict__)
            restricted_load(module_file.read(), module.__file__, tmp_globals)
            module.__dict__.update(tmp_globals)


def safe_find_spec(name, package=None, cache=None):
    """
    Find a module's spec.
    Modified from importlib
    """

    def _find_spec(name, path, target=None):
        meta_path = sys.meta_path
        if meta_path is None:
            # PyImport_Cleanup() is running or has been called.
            raise ImportError("sys.meta_path is None, Python is likely shutting down")

        if not meta_path:
            warn("sys.meta_path is empty")

        for finder in meta_path:
            spec = None
            try:
                find_spec = finder.find_spec
                spec = find_spec(name, path, target)
                if spec is not None:
                    return spec
            except AttributeError:
                loader = finder.find_module(name, path)
                if loader is not None:
                    spec = importlib.util.spec_from_loader(name, loader)
                    if spec is not None:
                        return spec
        else:
            return None

    fullname = (
        importlib.util.resolve_name(name, package) if name.startswith(".") else name
    )
    if fullname not in __SAFE_MODULES:
        parent_name = fullname.rpartition(".")[0]
        if parent_name:
            if parent_name in __SAFE_MODULES:
                parent = __SAFE_MODULES[parent_name]
            else:
                parent = safe_import(cache)(
                    parent_name, glob=globals(), fromlist=["__path__"]
                )
            try:
                parent_path = parent.__path__
            except AttributeError as error:
                raise ModuleNotFoundError(
                    f"__path__ attribute not found on {parent_name!r} "
                    f"while trying to find {fullname!r}",
                    name=fullname,
                ) from error
        else:
            parent_path = None
        return _find_spec(fullname, parent_path)

    module = __SAFE_MODULES[fullname]
    if module is None:
        return None
    try:
        spec = module.__spec__
    except AttributeError:
        raise ValueError("{}.__spec__ is not set".format(name)) from None
    else:
        if spec is None:
            raise ValueError("{}.__spec__ is None".format(name))
        return spec


__SAFE_MODULES: Dict[str, ModuleType] = {}


def restricted_load(code, filepath, _globals):
    byte_code, errors, warnings, names = compile_restricted_exec(
        code, filename=filepath, policy=Policy
    )
    if errors:
        raise SyntaxError(errors)
    for warning in warnings:
        if not warning.endswith("Prints, but never reads 'printed' variable."):
            warn(f"SyntaxWarning: {warning}")
    exec(byte_code, _globals, _globals)


def load_file(file):
    # Ensure that we never use the cached version of modinfo
    if "portmod.pybuild.modinfo" in sys.modules:
        del sys.modules["portmod.pybuild.modinfo"]

    filename, _ = os.path.splitext(os.path.basename(file))

    with open(file, "r") as module_file:
        code = module_file.read()
    try:
        tmp_globals = deepcopy(SAFE_GLOBALS)
        tmp_globals["__builtins__"]["__import__"] = safe_import()
        tmp_globals["__name__"] = filename
        restricted_load(code, file, tmp_globals)
        tmp_globals["Mod"].__pybuild__ = file
        mod = tmp_globals["Mod"]()
    except Exception as e:
        warn(e)
        if env.DEBUG:
            traceback.print_exc()
        warn('Could not load pybuild "{}"'.format(filename))
        if env.ALLOW_LOAD_ERROR:
            return None
        raise e
    mod.FILE = os.path.abspath(file)
    mod.INSTALLED = False
    return mod


def load_all_installed():
    """
    Returns every single installed mod in the form of a map from their simple mod name
    to their mod object
    """
    mods = {}
    repo = env.INSTALLED_DB

    for path in glob.glob(os.path.join(repo, "*/*")):
        mod = __load_installed_mod(path)
        if mod is not None:
            if mods.get(mod.MN) is None:
                mods[mod.MN] = [mod]
            else:
                mods[mod.MN].append(mod)
    return mods


def __load_installed_mod(path):
    if os.path.exists(path):
        files = glob.glob(os.path.join(path, "*.pybuild"))
        if len(files) > 1:
            atom = Atom(
                os.path.basename(os.path.dirname(files[0]))
                + "/"
                + os.path.basename(files[0].rstrip(".pybuild"))
            )
            raise Exception('Multiple versions of mod "{}" installed!'.format(atom))
        elif len(files) == 0:
            return None

        for file in files:
            if __mods.get(file, False):
                return __mods[file]
            else:
                mod = load_file(file)
                if mod is None:
                    continue

                mod.INSTALLED = True
                with open(os.path.join(path, "REPO"), "r") as repo_file:
                    mod.REPO = repo_file.readlines()[0].rstrip()
                    mod.DISPLAY_ATOM = mod.ATOM + "::" + mod.REPO
                with open(os.path.join(path, "USE"), "r") as use_file:
                    mod.INSTALLED_USE = set(use_file.readlines()[0].split())

                __mods[file] = mod
                return mod
    return None


# Loads mods from the installed database
def load_installed_mod(atom):
    repo = env.INSTALLED_DB

    path = None
    if atom.C:
        path = os.path.join(repo, atom.C, atom.MN)
    else:
        for dirname in glob.glob(os.path.join(repo, "*")):
            path = os.path.join(repo, dirname, atom.MN)
            if os.path.exists(path):
                break

    if path is not None:
        mod = __load_installed_mod(path)
    else:
        return None

    if mod is None or not atom_sat(mod.ATOM, atom):
        return None
    else:
        return mod


def load_mod(atom):
    """
    Loads all mods matching the given atom
    There may be multiple versions in different repos,
    as well versions with different version or release numbers
    """
    mods = []

    path = None
    for repo in env.REPOS:
        if not os.path.exists(repo.location):
            warn(
                "Repository {} does not exist at configured location {}".format(
                    repo.name, repo.location
                )
            )
            print(
                'You might need to run "omwmerge --sync" if this is a remote repository'
            )

        if atom.C:
            path = os.path.join(repo.location, atom.C, atom.MN)
        else:
            for category in get_categories(repo.location):
                path = os.path.join(repo.location, category, atom.MN)
                if os.path.exists(path):
                    break

        if path is not None and os.path.exists(path):
            for file in glob.glob(os.path.join(path, "*.pybuild")):
                if __mods.get(file, False):
                    mod = __mods[file]
                else:
                    mod = load_file(file)
                    if mod is None:
                        continue

                    mod.INSTALLED = False
                    __mods[file] = mod
                if atom_sat(mod.ATOM, atom):
                    mods.append(mod)
    return mods


def load_all():
    mods = []
    for repo in env.REPOS:
        for category in get_categories(repo.location):
            for file in glob.glob(
                os.path.join(repo.location, category, "*", "*.pybuild")
            ):
                if __mods.get(file, False):
                    mod = __mods[file]
                else:
                    mod = load_file(file)
                    if mod is None:
                        continue

                    __mods[file] = mod
                mods.append(mod)
    return mods
