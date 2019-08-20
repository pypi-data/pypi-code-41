__all__ = ['TBM']

from flake8_import_order.styles import Style
from natsort import natsorted


class TBM(Style):
	@staticmethod
	def import_key(import_):
		modules = [TBM.module_key(module) for module in import_.modules]
		names = [TBM.name_key(name) for name in import_.names]

		return (import_.type, import_.is_from, import_.level, modules, names)

	@staticmethod
	def module_key(name):
		return (name.lower(), name)

	@staticmethod
	def name_key(name):
		return (-name.isupper(), name)

	@staticmethod
	def sorted_names(names):
		return natsorted(names, key=TBM.name_key)
