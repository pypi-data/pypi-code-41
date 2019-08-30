import sys, os, re, logging
from os.path import dirname, basename, isabs, join, exists, isdir
from collections import namedtuple
from .imageutils import find_dependencies
import ctypes


DllList = namedtuple('DllList', 'found missing')

WHITELIST = re.compile(r'(api-ms|vcruntime|ucrtbase)')

MAX_PATH = 255


class DllFinder:
    def __init__(self, extensions, exclude=None, logger=None):
        self.extensions = extensions

        self.exclude = set(exclude or [])
        # A set of basenames (no paths) of DLLs to exclude.  We will add system DLLs to this
        # set (but no the original structure passed in).

        self.logger = logger or logging.getLogger('kelvin.dlls')

        self.windir = os.environ['WINDIR'].lower()

        self._pathcache = {}
        # Maps from lowercased filename to the fully qualified path.  We only get base names
        # from a DLL and a lot of DLLs will map to the same ones, so looking them up once
        # helps.

        self.found = set()
        # Fully qualified filenames of dependencies we've found.

        self.missing = set()
        # Base names of DLLs that could not be found.

        self.path = self._make_path()

    def _get_fully_qualified_path(self, filename):
        filename = filename.lower()

        if filename in self._pathcache:
            return self._pathcache[filename]

        if isabs(filename):
            self._pathcache[basename(filename)] = filename
            return filename

        if filename in self.missing:
            return None

        fqn = self._find_dll(filename)

        if fqn:
            self._pathcache[filename] = fqn
            return fqn

        self.missing.add(filename)
        return None

    def _find_dll(self, filename):
        """
        Searches the Windows and Python paths for the given DLL.
        """
        for dir in self.path:
            fqn = join(dir, filename)
            if exists(fqn) and not isdir(fqn):
                return fqn
        return None

    def _make_path(self):
        entries = [dirname(sys.executable)]
        entries.extend(os.environ['PATH'].split(';'))
        entries.extend(sys.path)

        seen = set()
        cleaned = []
        for entry in entries:
            lowered = entry.lower()
            if lowered in seen:
                continue

            if not isdir(lowered):
                if not lowered.endswith('.zip'):
                    self.logger.log(1, 'Invalid entry in path: %s', lowered)
                continue

            if lowered not in seen:
                seen.add(lowered)
                cleaned.append(entry)

        self.logger.log(1, 'DLL search path: %s', cleaned)

        return cleaned

    def find_dlls(self):
        """
        Finds the DLLs imported by (needed by) the extensions.

        extensions
          A list of modulefinder.Module objects for the Python extension DLLs.
        """
        images = []
        # The list of items to search for.  The initial items will have absolute paths, but
        # we'll add DLL names with no paths as we find depenencies.

        # Start with the Python DLL.
        images.append(GetPythonDLL())

        # Include any extensions, which are DLLs, that the analyzer found we need.
        # Include in the list of DLLs to copy (map_module_to_path) and also in the
        # list of images to look for dependencies for (images).

        for item in self.extensions:
            images.append(item.__file__)

        seen = set()
        # The images we've already processed, as fully qualified paths.  The same as the values
        # in map_module_to_path.

        while images:
            filename = images.pop(0)

            if basename(filename).lower() in seen:
                continue

            fqn = self._get_fully_qualified_path(filename)
            if not fqn:
                # This is a missing file and is added to self.missing.
                continue

            seen.add(basename(fqn).lower())

            if self._exclude(fqn):
                self.logger.debug('Excluding %s', filename)
                continue

            self.logger.debug('Analyzing %s', filename)

            info = find_dependencies(fqn)
            self.logger.log(1, 'Dependencies: image=%s info=%r', fqn, info)

            if info.issystem:
                # This is a system DLL and not one we should redistribute.
                self.logger.log(1, 'Excluding system file %s', fqn)
                self.excludes.add(basename(fqn).lower())
                continue

            for dep in info.dependencies:
                dep = dep.lower()
                if dep in seen:
                    continue
                images.append(dep)

            self.found.add(fqn)

        return DllList(list(self.found), list(self.missing))

    def _exclude(self, fqn):
        """
        Returns True if this DLL should be excluded.  We need to exclude during processing
        so we don't pick up dependencies of an excluded DLL.
        """
        assert isabs(fqn), "Not absolute: %s" % fqn
        fqn = fqn.lower()

        filename = basename(fqn)

        # Always include pyd files unless they have been explicitly excluded.  (I don't think
        # this can happen, but there is no sense in making it impossible.)
        if self.exclude and filename.endswith('.pyd'):
            return filename[:-4] in self.exclude

        if WHITELIST.match(filename):
            return False

        if fqn.startswith(self.windir):
            return True

        return False


_PYTHON_DLL = None  # cache


def GetPythonDLL():
    """
    Returns the name of the Python DLL (e.g. "python37") linked to the current Python interpreter.
    """
    global _PYTHON_DLL
    if not _PYTHON_DLL:
        _kernel32 = ctypes.windll.kernel32
        _kernel32.GetModuleFileNameA.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
        _kernel32.GetModuleFileNameA.restype = ctypes.c_ulong
        size = 1000
        buf = ctypes.create_string_buffer(size + 1)
        _kernel32.GetModuleFileNameA(sys.dllhandle, ctypes.byref(buf), size)
        _PYTHON_DLL = buf.value.decode('mbcs')

    return _PYTHON_DLL
