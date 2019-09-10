# -*- coding: utf-8 -*-
""" Revision utility routines """

import logging
_log = logging.getLogger(__name__)


def parse(l):
	try:
		aux = l.strip().split(".")
		n = len(aux)
		if n == 3:
			rev_major, rev_minor, rev_micro, = aux
		elif n == 2:
			rev_major, rev_minor, = aux
			rev_micro = 0
		elif n == 1:
			rev_major, = aux
			rev_minor = 0
			rev_micro = 0
		rev_major, rev_minor, rev_micro, = map(int, (
				rev_major,
				rev_minor,
				rev_micro,
		))
		return (
				rev_major,
				rev_minor,
				rev_micro,
		)
	except Exception:
		pass
	return None


def load(record_path):
	try:
		with open(record_path, "r") as fp:
			for l in fp:
				rev = parse(l)
				if rev is not None:
					return rev
		return (
				0,
				0,
				0,
		)
	except Exception:
		_log.exception("cannot reach record file: %r", record_path)
		raise


def build(rev_major, rev_minor, rev_micro):
	rev_text = "%d.%d.%d" % (
			rev_major,
			rev_minor,
			rev_micro,
	)
	return rev_text


def dump(record_path, rev_major, rev_minor, rev_micro):
	rev_text = build(rev_major, rev_minor, rev_micro)
	with open(record_path, "w") as fp:
		fp.write(rev_text)
		fp.write("\n")


BUMP_MAJOR = 2
BUMP_MINOR = 1
BUMP_MICRO = 0


def bump(bump_level, rev_major, rev_minor, rev_micro):
	if BUMP_MICRO == bump_level:
		rev_micro = rev_micro + 1
	elif BUMP_MINOR == bump_level:
		rev_minor = rev_minor + 1
		rev_micro = 0
	elif BUMP_MAJOR == bump_level:
		rev_major = rev_major + 1
		rev_minor = 0
		rev_micro = 0
	return (
			rev_major,
			rev_minor,
			rev_micro,
	)


def record_revision_history(history_path, rev_major, rev_minor, rev_micro, changeset_rev):
	rev_line = "%d.%d.%d\t%s\n" % (
			rev_major,
			rev_minor,
			rev_micro,
			changeset_rev,
	)
	with open(history_path, "a") as fp:
		fp.write(rev_line)


def iter_revision_history(history_path):
	with open(history_path, "r") as fp:
		for l in fp:
			aux = l.split("\t")
			rev = aux[0].strip()
			changeset_rev = aux[1].strip()
			yield (rev, changeset_rev)


def lookup_changeset_revision(history_path, changeset_rev):
	try:
		for l_rev, l_changeset_rev, in iter_revision_history(history_path):
			if l_changeset_rev == changeset_rev:
				return l_rev
	except Exception as e:
		_log.warning("cannot open revision history (%r): %r", e, history_path)
	return None
