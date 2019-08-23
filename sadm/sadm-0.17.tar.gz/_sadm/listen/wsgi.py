# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.listen import wapp

__all__ = ['application']

application = wapp.init()
