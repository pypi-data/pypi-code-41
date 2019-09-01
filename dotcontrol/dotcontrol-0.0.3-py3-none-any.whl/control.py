import toml
import subprocess as sp
from pathlib import Path
from .profile import Profile
from .util import keep_cwd, read_config, write_config, iterdirp


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
		
	def init(self):
		from .util import mkdirp
		from .const import CONTROL_CONFIG_TEMPLATE

		mkdirp(self.profiles_path)
		self.config = CONTROL_CONFIG_TEMPLATE.copy()
		self.current_profile = Profile.create(self, self.config['current_profile'])
		self.save()
	
	def load(self):
		self.config = read_config(self.config_path)
		self.current_profile = Profile.get(self, self.config['current_profile'])
	
	def save(self):
		write_config(self.config_path, self.config)

	def switch_profile(self, name):		
		self.current_profile.deactivate()
		self.current_profile = Profile.get(self, name) or Profile.create(self, name)
		self.current_profile.activate()
		self.save()

	def delete_profile(self, name):
		self.get_profile(name).delete()

	def iter_profiles(self):
		for item in self.profiles_path.iterdir():
			if item.is_dir():
				profile = Profile.get(self, item.name)
				if profile.exists:
					yield profile
