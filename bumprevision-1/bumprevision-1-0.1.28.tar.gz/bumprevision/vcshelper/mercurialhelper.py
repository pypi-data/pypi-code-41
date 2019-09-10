# -*- coding: utf-8 -*-
""" Mercurial helper routines """

from subprocess import check_output


def is_clean():
	data_stdout = check_output(("hg", "identify", "--id"))
	id_line = data_stdout.strip()
	if id_line[-1] == b"+":
		return False
	return True


def get_parent_rev():
	data_stdout = check_output(("hg", "parent", "--rev", "parents()", "--template", "{rev}:{node}\\n"))
	aux = data_stdout.split(b"\n")
	return aux[0].strip().decode('utf-8')


def get_current_rev():
	data_stdout = check_output(("hg", "parent", "--template", "{rev}:{node}\\n"))
	return data_stdout.strip().decode('utf-8')
