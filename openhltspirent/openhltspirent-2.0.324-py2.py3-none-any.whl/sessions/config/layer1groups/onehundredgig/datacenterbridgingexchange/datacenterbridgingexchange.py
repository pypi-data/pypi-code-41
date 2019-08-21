from openhltspirent.base import Base
class DataCenterBridgingExchange(Base):
	"""TBD
	"""
	YANG_NAME = 'data-center-bridging-exchange'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(DataCenterBridgingExchange, self).__init__(parent)

	def create(self):
		"""Create an instance of the `data-center-bridging-exchange` resource

		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `data-center-bridging-exchange` resource

		"""
		return self._delete()

