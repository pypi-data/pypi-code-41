class QueryBuilder:
    def __init__(self):
        self._object_name = None
        self._fields = []
        self._where = []
        self._order = []
        self._limit = None
        self._offset = None

    def from_(self, object_name):
        self._object = object_name

    def select(self, *fields):
        self.fields = fields