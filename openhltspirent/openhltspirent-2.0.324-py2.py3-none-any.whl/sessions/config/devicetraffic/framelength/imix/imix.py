from openhltspirent.base import Base
class Imix(Base):
	"""TBD
	"""
	YANG_NAME = 'imix'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"ImixType": "imix-type"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Imix, self).__init__(parent)

	@property
	def CustomImix(self):
		"""TBD

		Get an instance of the CustomImix class.

		Returns:
			obj(openhltspirent.sessions.config.devicetraffic.framelength.imix.customimix.customimix.CustomImix)
		"""
		from openhltspirent.sessions.config.devicetraffic.framelength.imix.customimix.customimix import CustomImix
		return CustomImix(self)

	@property
	def ImixType(self):
		"""TBD

		Getter Returns:
			DEFAULT | CUSTOM_IMIX

		Setter Allows:
			DEFAULT | CUSTOM_IMIX

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('imix-type')

	def update(self, ImixType=None):
		"""Update the current instance of the `imix` resource

		Args:
			ImixType (enumeration): TBD
		"""
		return self._update(locals())

