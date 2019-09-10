# -*- coding: utf-8 -*-
""" Bump revision """

import sys
import os
import getopt
import re
import logging

from bumprevision.vcshelper import get_helper as get_vcs_helper
from bumprevision import revision

_log = logging.getLogger(__name__)

REV_RECORD_FILE = ".revision.txt"
REV_TARGET_FILE = ".revbump-filelist.txt"
REV_HISTORY_FILE = ".revbump-history.txt"

DEVELOPMENT_BUMP = -1  # use a number not used by revision.bump()

_HELP_TEXT = """
Argument: [Options...]

Options:
	--help
		Print this help message.
	--micro | --patch | -r | -p
		Bump micro-part of revision number.
	--minor | -m
		Bump minor-part of revision number.
		Will reset micro-part of revision number to 0.
	--major | -M
		Bump major-part of revision number.
		Will reset both minor-part and micro-part of revision number to 0.
	--set-revision=[REVISION] | --rev=[REVISION]
		Set revision to given value.
	--drop-removed
		Delete unreachable files from file list.
""".replace("\t", "    ")


def _load_filelist():
	filelist = []
	try:
		with open(REV_TARGET_FILE, "r") as fp:
			for content_line in fp:
				content_line = content_line.strip()
				if content_line:
					filelist.append(content_line)
	except Exception as e:
		_log.warning("failed on loading file list (%r): %r", e, REV_TARGET_FILE)
	return filelist


def _dump_filelist(file_set):
	with open(REV_TARGET_FILE, "w") as fp:
		for f in file_set:
			fp.write(f)
			fp.write("\n")


def _append_new_to_filelist(file_set, file_list_to_append):
	file_set_changed = False
	for f in file_list_to_append:
		f = os.path.realpath(f)
		if not os.path.isfile(f):
			_log.warning("file not exist: %r", f)
			continue
		f = os.path.relpath(f)
		file_set.append(f)
		file_set_changed = True
	return file_set_changed


def _filter_unreachable_from_filelist(file_set):
	to_remove = []
	file_set = set(file_set)
	for f in file_set:
		if not os.path.isfile(f):
			to_remove.append(f)
			_log.info("drop unaccessible file: %r", f)
	if to_remove:
		file_set = file_set - set(to_remove)
		return file_set, True
	return file_set, False


# pylint: disable=too-many-locals
def _parse_option(argv):
	current_rev_major, current_rev_minor, current_rev_micro, = revision.load(REV_RECORD_FILE)
	file_set = _load_filelist()
	bump_level = 0
	force_run = False
	drop_removed = False
	file_set_changed = False
	try:
		opts, args, = getopt.getopt(argv, "rpmMDfh", (
				"micro",
				"patch",
				"minor",
				"major",
				"dev",
				"force",
				"drop-removed",
				"rev=",
				"set-revision=",
				"set-version=",
				"help",
		))
		for opt, arg, in opts:
			if opt in ("-r", "-p", "--micro", "--patch"):
				bump_level = max(bump_level, revision.BUMP_MICRO)
			elif opt in ("-m", "--minor"):
				bump_level = max(bump_level, revision.BUMP_MINOR)
			elif opt in ("-M", "--major"):
				bump_level = max(bump_level, revision.BUMP_MAJOR)
			elif opt in ("-D", "--dev"):
				bump_level = DEVELOPMENT_BUMP
			elif opt in ("-f", "--force"):
				force_run = True
			elif opt in ("--drop-removed", ):
				drop_removed = True
			elif opt in ("--rev", "--set-revision", "--set-version"):
				rev = revision.parse(arg)
				if rev is None:
					_log.error("cannot parse revision number parts from given revision text: [%r]", arg)
					sys.exit(1)
				current_rev_major, current_rev_minor, current_rev_micro, = rev
			elif opt in ("-h", "--help"):
				sys.stdout.write(_HELP_TEXT + "\n")
				sys.exit(1)
		file_set_changed = _append_new_to_filelist(file_set, args)
	except Exception as e:
		_log.exception("Argument error: [%r]. Pass -h or --help for usage help.", e)
		sys.exit(1)
	if drop_removed:
		file_set, aux, = _filter_unreachable_from_filelist(file_set)
		file_set_changed = file_set_changed or aux
	file_set = list(sorted(set(file_set)))
	if file_set_changed:
		_dump_filelist(file_set)
	return (
			current_rev_major,
			current_rev_minor,
			current_rev_micro,
			bump_level,
			force_run,
			file_set,
	)


_REVLITERAL_TRAP = re.compile(r"""^([A-Za-z0-9\s_:&\*']+)(:?=:?)\s*([\"\']?([a-fnorsv0-9,;:\.\s-]*)["']?)?\s*([,;:])?\s*"""
								r"""(#|//|/*)\s+REV-CONSTANT:([a-z-]+) 5d022db7d38f580a850cd995e26a6c2f""")


# pylint: disable=too-many-arguments
def _build_content_line(mode, l_prefix, l_assignment_operator, l_suffix, l_comment_mark, rev_major, rev_minor, rev_micro, changeset_rev, dev_bumping_mode):
	if mode == "rev":
		if dev_bumping_mode:
			c = "\"%d.%d.%d.dev-%s\"" % (
					rev_major,
					rev_minor,
					rev_micro,
					changeset_rev[:8],
			)
		else:
			c = "\"%d.%d.%d\"" % (
					rev_major,
					rev_minor,
					rev_micro,
			)
	elif mode == "changeset":
		c = "\"%s\"" % (changeset_rev, )
	elif mode == "rev-major":
		c = str(rev_major)
	elif mode == "rev-minor":
		c = str(rev_minor)
	elif mode == "rev-micro":
		c = str(rev_micro)
	else:
		if dev_bumping_mode:
			c = "\"%d.%d.%d.dev-%s; %s\"" % (
					rev_major,
					rev_minor,
					rev_micro,
					changeset_rev[:8],
					changeset_rev,
			)
		else:
			c = "\"%d.%d.%d; %s\"" % (
					rev_major,
					rev_minor,
					rev_micro,
					changeset_rev,
			)
	l_assign_padding = " " if (l_prefix[-1] == " ") else ""
	l_prefix = l_prefix.rstrip()
	if not l_suffix:
		l_suffix = ''
	if l_comment_mark == "/*":
		trap_text = "\t/* REV-CONSTANT:%s 5d022db7d38f580a850cd995e26a6c2f */" % (mode, )
	else:
		trap_text = "\t%s REV-CONSTANT:%s 5d022db7d38f580a850cd995e26a6c2f" % (
				l_comment_mark,
				mode,
		)
	return l_prefix + l_assign_padding + l_assignment_operator + l_assign_padding + c + l_suffix + trap_text


# pylint: disable=too-many-arguments
def _replace_revision_content(filepath, rev_major, rev_minor, rev_micro, changeset_rev, dev_bumping_mode):
	result = []
	# -- read
	with open(filepath, "r") as fp:
		for content_line in fp:
			content_line = content_line.rstrip()
			m = _REVLITERAL_TRAP.match(content_line)
			if m is not None:
				l_prefix = m.group(1)
				l_assignment_operator = m.group(2)
				l_suffix = m.group(5)
				l_comment_mark = m.group(6)
				l_mode = m.group(7)
				content_line = _build_content_line(l_mode, l_prefix, l_assignment_operator, l_suffix, l_comment_mark, rev_major, rev_minor, rev_micro,
													changeset_rev, dev_bumping_mode)
			result.append(content_line)
	# -- strip empty lines
	content_line = result.pop()
	while not content_line:
		content_line = result.pop()
	result.append(content_line)
	# -- write
	with open(filepath, "w") as fp:
		for content_line in result:
			fp.write(content_line)
			fp.write("\n")


def main():
	logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
	argv = sys.argv[1:]
	current_rev_major, current_rev_minor, current_rev_micro, bump_level, force_run, file_list, = _parse_option(argv)
	vcshelper = get_vcs_helper()
	dev_bumping_mode = True if (DEVELOPMENT_BUMP == bump_level) else False
	is_workcopy_clean = vcshelper.is_clean()
	if not is_workcopy_clean:
		if dev_bumping_mode:
			_log.warning("work copy is not clean. bumping anyway since development bump mode is enabled.")
		elif force_run:
			_log.warning("work copy is not clean. force bumping.")
		else:
			_log.info("work copy is not clean. stop bumping revision.")
			return
	known_rev_text = revision.lookup_changeset_revision(REV_HISTORY_FILE, vcshelper.get_parent_rev())
	if known_rev_text and ((not dev_bumping_mode) or is_workcopy_clean):
		_log.info("current work copy is step on revision: %r. stop bumping revision.", known_rev_text)
		return
	changeset_rev = vcshelper.get_current_rev()
	if dev_bumping_mode:
		updated_rev_major, updated_rev_minor, updated_rev_micro, = revision.parse(known_rev_text) if known_rev_text else (
				current_rev_major,
				current_rev_minor,
				current_rev_micro,
		)
	else:
		updated_rev_major, updated_rev_minor, updated_rev_micro, = revision.bump(bump_level, current_rev_major, current_rev_minor, current_rev_micro)
		_log.info("bump to revision %d.%d.%d at %r", updated_rev_major, updated_rev_minor, updated_rev_micro, changeset_rev)
	for f in file_list:
		_replace_revision_content(f, updated_rev_major, updated_rev_minor, updated_rev_micro, changeset_rev, dev_bumping_mode)
		_log.info("updated %r", f)
	if not dev_bumping_mode:
		revision.record_revision_history(REV_HISTORY_FILE, updated_rev_major, updated_rev_minor, updated_rev_micro, changeset_rev)
		revision.dump(REV_RECORD_FILE, updated_rev_major, updated_rev_minor, updated_rev_micro)
		_log.info("updated revision history and revision record.")
	_log.info("version bumped %d.%d.%d => %d.%d.%d", current_rev_major, current_rev_minor, current_rev_micro, updated_rev_major, updated_rev_minor,
				updated_rev_micro)


if __name__ == "__main__":
	main()

_rev_full = "0.1.28; 5f1d9edb08913f7cbb131251d0817ddc8353b5ce"  # REV-CONSTANT:full 5d022db7d38f580a850cd995e26a6c2f
_rev_text = "0.1.28"  # REV-CONSTANT:rev 5d022db7d38f580a850cd995e26a6c2f
_rev_changeset = "5f1d9edb08913f7cbb131251d0817ddc8353b5ce"  # REV-CONSTANT:changeset 5d022db7d38f580a850cd995e26a6c2f
_rev_major = 0  # REV-CONSTANT:rev-major 5d022db7d38f580a850cd995e26a6c2f
_rev_minor = 1  # REV-CONSTANT:rev-minor 5d022db7d38f580a850cd995e26a6c2f
_rev_micro = 28  # REV-CONSTANT:rev-micro 5d022db7d38f580a850cd995e26a6c2f

# vim: ts=4 sw=4 foldmethod=marker ai nowrap
