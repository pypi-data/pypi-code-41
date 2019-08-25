# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import path, makedirs

def test_deploy_testing(testing_plugin):
	makedirs(path.join('tdata', 'deploy', 'plugin'), exist_ok = True)
	p = testing_plugin('testing', ns = '_sadmtest', deploy = True)
	print('-- deploy plugin: testing')
	p.deploy()

def test_all_deploy(testing_plugin):
	makedirs(path.join('tdata', 'deploy', 'plugin'), exist_ok = True)
	t = testing_plugin(ns = '_sadmtest', deploy = True, buildDeploy = False)
	for opt in t._env.config.options('deploy'):
		if opt.startswith('env.'):
			pname = '.'.join(opt.split('.')[1:])
			if pname == 'testing':
				continue
			p = testing_plugin(pname, deploy = True)
			print('-- deploy plugin:', pname)
			p.deploy()
