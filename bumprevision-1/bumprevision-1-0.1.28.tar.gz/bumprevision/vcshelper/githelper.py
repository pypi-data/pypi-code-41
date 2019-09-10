# -*- coding: utf-8 -*-
""" Git helper routines """

from subprocess import call, check_output


def is_clean():
	retcode = call(("git", "diff", "--quiet"))
	if retcode == 0:
		return True
	if retcode == 1:
		return False
	raise ValueError("unrecognized return code: %r" % (retcode, ))


def get_parent_rev():
	data_stdout = check_output(("git", "rev-parse", "HEAD^"))
	return data_stdout.strip().decode('utf-8')


def get_current_rev():
	data_stdout = check_output(("git", "rev-parse", "HEAD"))
	return data_stdout.strip().decode('utf-8')
