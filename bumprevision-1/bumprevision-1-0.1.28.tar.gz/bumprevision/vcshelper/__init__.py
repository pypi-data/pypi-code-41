# -*- coding: utf-8 -*-
""" VCS Helper """

from os.path import isdir
from collections import namedtuple

VCSHelper = namedtuple("VCSHelper", (
		"is_clean",
		"get_parent_rev",
		"get_current_rev",
))


def _mercurial_helper():
	from bumprevision.vcshelper.mercurialhelper import is_clean, get_parent_rev, get_current_rev
	return VCSHelper(is_clean, get_parent_rev, get_current_rev)


def _get_helper():
	from bumprevision.vcshelper.githelper import is_clean, get_parent_rev, get_current_rev
	return VCSHelper(is_clean, get_parent_rev, get_current_rev)


def get_helper():
	if isdir(".hg"):
		return _mercurial_helper()
	if isdir(".git"):
		return _get_helper()
	raise ValueError("require mercurial or git")
