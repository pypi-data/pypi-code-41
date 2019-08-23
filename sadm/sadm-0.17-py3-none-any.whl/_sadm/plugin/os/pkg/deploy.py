# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from .debian import deploy as debian

__all__ = ['deploy']

def deploy(env):
	dn = env.dist()
	if dn == 'debian':
		debian.deploy(env)
	else:
		env.error("unsupported dist %s" % dn)
