# -*- coding: utf-8 -*-
"""
    flest.config
    ~~~~~~~~~~~~

    enhanced Config class
"""
try:
    import yaml
    import errno
    import os
    import types
    import flask
    from ._utils import _unwind


    class Config(flask.Config):
        def from_dict(self, d: dict, **kwargs):
            """Updates the config by unwinding a dicts and capitalizing all the
            keys, recursively.
            """
            d.update(kwargs)
            self.from_mapping(_unwind(d))
            return True

        def from_yamlfile(self, filename, silent=False):
            """Updates the values in the config from a YAML file. Lower case
            config key names in YAML will be converted to uppercases.
            Also, dict style will be all unwinded to flat config keys
            :meth:`from_object` function.

            :param filename: the filename of the yaml config file.  This can 
                            either be an absolute filename or a filename 
                            relative to the root path.
            :param silent: set to ``True`` if you want silent failure for
                            missing files.
            """
            filename = os.path.join(self.root_path, filename)
            try:
                with open(filename, mode="rb") as f:
                    cf = yaml.load(f, Loader=yaml.FullLoader)
                    self.from_dict(cf)
            except IOError as e:
                if silent and e.errno in (errno.ENOENT, errno.EISDIR, errno.ENOTDIR):
                    return False
                e.strerror = "Unable to load configuration file (%s)" % e.strerror
                raise
            return True

        def __getitem__(self, key):
            x = super().__getitem__(key)
            if isinstance(x, list) and len(x) == 1:
                x = x[0]
            return x

        def __getattr__(self, key):
            key = key.upper()
            try:
                x = self.__getitem__(key)
            except Exception:
                x = None
            return x
except Exception:
    from flask import Config
