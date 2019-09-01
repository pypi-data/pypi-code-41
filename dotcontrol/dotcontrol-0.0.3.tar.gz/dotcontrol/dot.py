import os
from pathlib import Path
from shutil import rmtree
from .util import link_dir, iterdirp, mkdirp, now, sha1_hash, sha1_hash_dir
from .const import DOT_DATA_TEMPLATE


class Dot:
	def __init__(self, profile, path):
		self.profile = profile
		self.resolve_path(path)

		if self.normalized_origin_path in profile.config['dots']:
			self.load()

	def load(self):
		self.data = self.profile.config['dots'][self.normalized_origin_path]
	
	def save(self):
		self.profile.save()
	
	def create(self):
		if self.normalized_origin_path not in self.profile.config['dots']:
			self.data = self.profile.config['dots'][self.normalized_origin_path] = DOT_DATA_TEMPLATE.copy()
			if self.absolute_origin_path.is_dir():
				self.data['type'] = 'dir'
			elif self.absolute_origin_path.is_file():
				self.data['type'] = 'file'
		self.update_sha1_check()
		self.save()

	def resolve_path(self, raw_origin_path):
		self.raw_origin_path = raw_origin_path
		self.absolute_origin_path = Path(raw_origin_path).expanduser().resolve()

		try:
			relative_to_home = self.absolute_origin_path.relative_to(self.profile.control.user_home)
			self.normalized_origin_path = Path('~').joinpath(relative_to_home).as_posix()
			self.dot_path = self.profile.dot_home_path.joinpath(relative_to_home)
		except:
			self.normalized_origin_path = self.absolute_origin_path.as_posix()
			self.dot_path = self.profile.dot_root_path.joinpath(self.normalized_origin_path)

	def link_dot(self):
		'''Link origin to dot path.'''

		mkdirp(self.dot_path.parent)

		if self.dot_exists:
			self.dot_path.unlink()
		
		if self.type == 'file':
			os.link(self.absolute_origin_path, self.dot_path)
		elif self.type == 'dir':
			link_dir(self.absolute_origin_path, self.dot_path)

		self.update_sha1_check()
		self.save()

	def link_back(self, overwrite=False):
		'''Link dot back to origin, for actions like activating a profile.'''

		if self.origin_exists:
			if overwrite:
				self.absolute_origin_path.unlink()
			else:
				raise Exception('Origin {} already exists!'.format(self.normalized_origin_path))

		if self.type == 'file':
			os.link(self.dot_path, self.absolute_origin_path)
		elif self.type == 'dir':
			link_dir(self.dot_path, self.absolute_origin_path)
		
		self.update_sha1_check()
		self.save()

	def unlink(self):
		if self.dot_exists:
			if self.type == 'file':
				self.dot_path.unlink()
			elif self.type == 'dir':
				rmtree(self.dot_path)
		
	def delete(self):
		self.unlink()
		self.profile.config['dots'].pop(self.normalized_origin_path, None)
		self.save()

	def sha1_hash(self):
		if self.type == 'file':
			return sha1_hash(self.absolute_origin_path)
		elif self.type == 'dir':
			return sha1_hash_dir(self.absolute_origin_path)
	
	def update_sha1_check(self):
		self.data['sha1'] = self.sha1_hash()
		self.data['last_sha1_check'] = now()

	@property
	def changed(self):
		if self.type == 'file':
			return self.sha1_hash() != self.data['sha1']
		elif self.type == 'dir':
			walked_items = []
			for item in iterdirp(self.absolute_origin_path, files_only=True):
				item_relative = item.relative_to(self.absolute_origin_path).as_posix()
				if item_relative not in self.data['sha1']:
					return True
				else:
					if sha1_hash(item) != self.data['sha1'][item_relative]:
						return True
				walked_items.append(item_relative)
			for item in self.data['sha1']:
				if item not in walked_items:
					return True
		return False

	@property
	def origin_exists(self):
		return self.absolute_origin_path.exists()
	
	@property
	def dot_exists(self):
		return self.dot_path.exists()

	@property
	def type(self):
		return self.data['type']
	
	@type.setter
	def type(self, value):
		self.data['type'] = value
