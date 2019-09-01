from .dot import Dot


class Profile:
	def __init__(self, control, name, create=True):
		self.control, self.name = control, name
		self.root_path = control.profiles_path.joinpath(name)
		self.dot_root_path = self.root_path.joinpath('root')
		self.dot_home_path = self.root_path.joinpath('home')

		if name in control.config['profiles']:
			self.load()
		else:
			if create:
				self.create()
			else:
				raise Exception('profile {} does not exist'.format(name))
	
	def create(self):
		from .const import PROFILE_CONFIG_TEMPLATE
		from .util import mkdirp
		mkdirp(self.dot_root_path)
		mkdirp(self.dot_home_path)
		self.control.config['profiles'][self.name] = self.config = PROFILE_CONFIG_TEMPLATE.copy()
		self.save()
	
	def remote_setup(self, type, name=None, *args):
		if type == 'git':
			if not name:
				from os.path import basename
				name = basename(name)
				if name.endswith('.git'):
					name = name[:-4]
			remote = args[0]

			with keep_cwd(self.control.root_path):
				sp.run(['git', 'submodule', 'add', remote, name], check=True)
				sp.run(['git', 'add', '.'])
		
		self.control.config['profiles'][self.name] = self.config = PROFILE_CONFIG_TEMPLATE.copy()
		self.config['sync_type'] = type
		self.config['sync_remote'] = remote
		self.save()

	def load(self):
		self.config = self.control.config['profiles'][self.name]
	
	def save(self):
		self.control.save()
	
	def delete(self):
		if self.config['sync_type'] == 'git':
			from .util import delete_git_submodule
			relative_path = self.root_path.relative_to(self.control.root_path)
			delete_git_submodule(self.control.root_path, relative_path)
		elif self.config['sync_type'] == 'local':
			from shutil import rmtree
			rmtree(self.root_path)
		
		del self.control.config['profiles'][self.name]
		self.control.save()

	def set_dot(self, path):
		dot = Dot(self, path)
		dot.update_sha1_check()
		self.save()
		if not dot.dot_exists or dot.type == 'dir' and dot.changed:
			dot.link_dot()
		return dot

	def delete_dot(self, path):
		Dot(self, path, create=False).delete()
	
	def get_dot(self, path):
		return Dot(self, path, create=False)

	def iter_dots(self):
		for path in self.config['dots']:
			yield self.get_dot(path)

	def activate(self):
		for dot in self.iter_dots():
			dot.link_back()
		
		self.control.config['current_profile'] = self.name
		self.save()

	def deactivate(self):
		for dot in self.iter_dots():
			if dot.changed:
				raise Exception('{} has been changed and not committed yet!'.format(dot.normalized_origin_path))
	
	def update_dot_checks(self):
		for dot in self.iter_dots():
			dot.update_sha1_check()
