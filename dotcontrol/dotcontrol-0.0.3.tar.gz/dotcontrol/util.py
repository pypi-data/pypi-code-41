import subprocess as sp
from time import time
from datetime import datetime
from os import getcwd, chdir, link, path
from hashlib import sha1
from pathlib import Path
from shutil import rmtree
import toml


FILE_READ_CHUNK_SIZE = 4096


def read_config(path):
	try:
		return toml.loads(path.read_text())
	except:
		pass


def write_config(path, data):
	path.write_text(toml.dumps(data))


def now():
	return int(time())


def timestamp2iso(ts):
	# YYYY-MM-DDTHH:MM:SS
	return datetime.fromtimestamp(ts).isoformat()[:19]


def mkdirp(dest):
	'''
	Create directory, and its parent(s) if they did't exist,
	like `mkdir -p`.
	'''

	if not dest.exists():
		for parent in reversed(dest.parents):
			if not parent.exists():
				parent.mkdir()
		dest.mkdir()


def iterdirp(path, files_only=False, dirs_only=False, ignore_errors=False):
	'''Recursively iterate over directories and files under `path`.'''

	dirs = [path]
	dir = None
	while dirs:
		dir = dirs.pop(0)
		try:
			for item in dir.iterdir():
				if item.is_dir():
					dirs.append(item)
					if files_only:
						continue
				elif item.is_file() and dirs_only:
					continue
				yield item
		except Exception as e:
			if ignore_errors:
				pass
			else:
				raise e


class keep_cwd:
	'''
	Use `with keep_cwd(optional_target_path)` to go back to `cwd` after
	working in other directory(-ies).
	'''

	def __init__(self, to=None):
		self.to = to

	def __enter__(self):
		self.cwd = getcwd()
		if self.to:
			chdir(self.to)
	
	def __exit__(self, *args, **kwargs):
		chdir(self.cwd)


def link_dir(source, target):
	'''Recursively create directory structure and hard link files.'''

	for item in iterdirp(source):
		if not item.is_dir():
			item_target = target.joinpath(item.relative_to(source))
			mkdirp(item_target.parent)
			link(item, item_target)


def sha1_hash(object):
	'''
	Calculate hex digest for input.
	Argument may be a string, bytes object, or a path-like object.
	'''
	
	if type(object) in (str, bytes):
		return sha1(object).hexdigest()
	path = Path(object)
	if path.exists():
		with open(object, 'rb') as f:
			hash = sha1()
			buf = f.read(FILE_READ_CHUNK_SIZE)
			while buf:
				hash.update(buf)
				buf = f.read(FILE_READ_CHUNK_SIZE)
			return hash.hexdigest()


def sha1_hash_dir(path):
	'''
	Calculate sha1 hash for all files under given directory.
	Argument is instance of pathlib.Path.
	'''

	hashes = {}
	for item in iterdirp(path):
		if item.is_file():
			hashes[item.relative_to(path).as_posix()] = sha1_hash(item)
	return hashes


def compare_files_in_chunks(a, b):
	'''Compare two files in chunks to determine if they differ.'''

	with open(a, 'rb') as a, open(b, 'rb') as b:
		buf_a, buf_b = None, None
		while buf_a == buf_b and len(buf_a) > 0:
			buf_a = a.read(FILE_READ_CHUNK_SIZE)
			buf_b = b.read(FILE_READ_CHUNK_SIZE)
		if len(buf_a) == 0 and len(buf_b) == 0:
			return False
		elif buf_a != buf_b:
			return True
