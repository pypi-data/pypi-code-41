# encoding:utf8
from lupa import _lupa as lupaerr
from lupa import LuaRuntime
import os
import sys
import shutil
import logging
logging.basicConfig(level=logging.INFO)


LUACODE_INITCFG = '''
    package.path = package.path..";{tpath}/?"
    require ("{cfgf}")
'''


class LuabaseTool:

    _luabin = None
    _luagval = None

    _tmpdir = None

    def __init__(self):
        self.__init_luaenv()

    def lua_dofile(self, luaf):
        tpath = os.path.abspath(os.path.dirname(luaf))
        cfgf = luaf.split(os.sep)[-1]
        self.lua_dostring(LUACODE_INITCFG.format(
            tpath=tpath, cfgf=cfgf))
        self._luagval = self._luabin.globals()

    def __init_luaenv(self):
        self._luabin = LuaRuntime()

    def raise_err(self, errdesc):
        logging.error(errdesc)
        sys.exit()

    def lua_dostring(self, tarstr):
        logging.debug("run lua code:%s", tarstr)
        try:
            ret = self._luabin.execute(tarstr)
            return ret
        except lupaerr.LuaError as lerr:
            self.raise_err("Raise lua error! tracebck is->\n%s" % lerr)

    def lua_val(self, key):
        if not self._luagval:
            return None
        return self._luagval[key]

    def crt_tempdir(self, tmpdir):
        if os.path.isdir(tmpdir):
            shutil.rmtree(tmpdir)
        logging.info("Create the temporary dirpath->%s", tmpdir)
        os.makedirs(tmpdir)
        self._tmpdir = tmpdir
        return tmpdir

    def del_tempdir(self):
        if os.path.isdir(self._tmpdir):
            shutil.rmtree(self._tmpdir)

    def get_tempdir(self):
        return self._tmpdir


__all__ = [
    "LuabaseTool"
]
