import toml
import subprocess as sp
from pathlib import Path
from .profile import Profile
from .util import keep_cwd


class Control:
	def __init__(self):
		self.user_home = Path.home()
		self.root_path = self.user_home.joinpath('.config/dotcontrol')
		self.config_path = self.root_path.joinpath('config.toml')
		self.profiles_path = self.root_path.joinpath('profiles')
		
		if self.root_path.exists():
			self.load()
		else:
			self.init()
		
		self.current_profile = self.get_profile(self.config['current_profile'], create=True)
	
	def init(self):
		from .const import DEFAULT_CONFIG
		from .util import mkdirp
		mkdirp(self.profiles_path)
		self.config = DEFAULT_CONFIG.copy()
		self.setup_profile(self.config['current_profile'])
		self.save()
	
	def load(self):
		self.config = toml.loads(self.config_path.read_text())
	
	def save(self):
		self.config_path.write_text(toml.dumps(self.config))

	def setup_profile(self, name, sync_type=None, sync_args=None):
		if not sync_type:
			Profile(self, name, create=True).create()
		else:
			profile = Profile(self, name, create=False)
			profile.remote_setup(sync_type, sync_args)

	def get_profile(self, name, create=False):
		return Profile(self, name, create=create)

	def switch_profile(self, name):		
		self.current_profile.deactivate()
		self.current_profile = self.get_profile(name, create=True)
		self.current_profile.activate()

	def delete_profile(self, name):
		self.get_profile(name, create=False).delete()

	def iter_profiles(self):
		for name in self.config['profiles']:
			yield self.get_profile(name)
	
	def pull_remote_profiles(self):
		if self.config['sync_type'] == 'git':
			self.sync_command('submodule', 'update', '-f', '--')
	
	def set_dot(self, path):
		self.current_profile.set_dot(path)
	
	def delete_dot(self, path):
		self.current_profile.delete_dot(path)
	
	def commit_changes(self, message=None, all=True, *args):
		for profile in self.iter_profiles():
			profile.update_dot_checks()

		if all:
			self.sync_command('add', '.')

		if self.config['sync_type'] == 'git':
			if message:
				self.sync_command('commit', '-am', message, *args)
			else:
				self.sync_command('commit', *args)

	def set_sync(self, type, *args):
		self.config['sync_type'] = type
		if type == 'git':
			self.config['sync_program'] = type
			self.config['sync_remote'] = args[0]
			self.sync_command('init')
			try:
				self.sync_command('remote', 'add', 'sync', args[0])
			except:
				self.sync_command('remote', 'set-url', 'sync', args[0])
			self.sync_command('add', '.')
			self.commit_changes(message='set up sync')
			self.sync_command('push', '-u', 'sync', 'master')

		self.save()
	
	def sync_command(self, *args):
		if 'sync_program' not in self.config:
			raise Exception('Sync program not configured.')
		with keep_cwd(self.root_path):
			sp.run([self.config['sync_program']] + list(args))

	def sync_pull(self, *args):
		if 'sync_program' not in self.config:
			raise Exception('Sync program not configured.')
		
		if self.config['sync_type'] == 'git':
			self.sync_command('pull', *args)
			self.pull_remote_profiles()
	
	def sync_push(self, *args):
		if 'sync_program' not in self.config:
			raise Exception('Sync program not configured.')
		
		if self.config['sync_type'] == 'git':
			self.sync_command('push', *args)
	
