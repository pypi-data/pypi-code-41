import toml
from .dot import Dot
from .util import mkdirp, read_config, write_config
from .remote import get_remote
from .const import PROFILE_CONFIG_TEMPLATE


class Profile:
	@classmethod
	def get(cls, control, name):
		paths = cls.resolve_path(control, name)
		if paths['config_path'].exists():
			return cls(control, name)

	@classmethod
	def create(cls, control, name, *args, **kwargs):
		paths = cls.resolve_path(control, name)
		mkdirp(paths['dot_root_path'])
		mkdirp(paths['dot_home_path'])

		write_config(paths['config_path'], PROFILE_CONFIG_TEMPLATE.copy())

		return cls(control, name)
	
	@classmethod
	def resolve_path(cls, control, name):
		root_path = control.profiles_path.joinpath(name)
		return {
			'root_path': root_path,
			'config_path': root_path.joinpath('dotcontrol.toml'),
			'dot_root_path': root_path.joinpath('root'),
			'dot_home_path': root_path.joinpath('home')
		}
	
	@classmethod
	def create_from_remote(cls, control, type, remote_location, name=None, *args):
		remote = get_remote(type)

		if not name:
			name = remote.get_name(remote_location, *args)

		config_path = cls.resolve_path(control, name)['config_path']
		config = read_config(config_path)
		if not config:
			config = PROFILE_CONFIG_TEMPLATE.copy()
		config['sync_type'] = type

		remote.create_from(control, remote_location, name, config, *args)
		
		write_config(config_path, config)
		
	def __init__(self, control, name):
		self.control, self.name = control, name
		self.__dict__.update(self.resolve_path(control, name))

		if not self.exists:
			raise Exception('Profile {} does not exist'.format(name))
		try:
			self.load()
		except:
			raise Exception('Profile {} failed reading configuration file'.format(name))
		
		self.remote = get_remote(self.config['sync_type'])
		
	@property
	def exists(self):
		return self.config_path.exists()

	def load(self):
		self.config = read_config(self.config_path)
	
	def save(self):
		write_config(self.config_path, self.config)
	
	def delete(self):
		from shutil import rmtree
		rmtree(self.root_path)

	def set_dot(self, path):
		dot = Dot(self, path)
		dot.create()
		self.save()
		if not dot.dot_exists or dot.type == 'dir' and dot.changed:
			dot.link_dot()
		return dot

	def delete_dot(self, path):
		Dot(self, path).delete()
	
	def get_dot(self, path):
		return Dot.get(self, path)

	def iter_dots(self):
		for path in self.config['dots']:
			yield Dot(self, path)

	def activate(self):
		for dot in self.iter_dots():
			dot.link_back()
		
		self.control.config['current_profile'] = self.name
		self.save()

	def deactivate(self):
		for dot in self.iter_dots():
			if dot.changed:
				raise Exception('{} has been changed and not committed yet!'.format(dot.normalized_origin_path))
	
	def update_dot_sha1_checks(self):
		for dot in self.iter_dots():
			dot.update_sha1_check()
		self.save()
	
	def sync_setup(self, type, remote_location, *args):
		self.remote = get_remote(type)
		self.remote.setup(self, remote_location, self.config, *args)
		self.save()

	def sync_command(self, *args):
		return self.remote.command(self, *args)

	def sync_commit(self, *args):
		self.update_dot_sha1_checks()
		return self.remote.commit(self, *args)
	
	def sync_pull(self, *args):
		return self.remote.pull(self, *args)

	def sync_push(self, *args):
		return self.remote.push(self, *args)
