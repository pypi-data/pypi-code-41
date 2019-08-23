# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.utils import systemd

__all__ = ['deploy']

def deploy(env):
	systemd.restart('netfilter-persistent')
