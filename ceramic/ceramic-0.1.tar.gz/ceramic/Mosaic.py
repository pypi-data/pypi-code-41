from pandas import concat, DataFrame
from abstract import Graph
from .TileRow import TileRow


class Mosaic:
	def __init__(self, data, columns=None, rows=None, label=None, _parent=None):
		"""
		:type data: DataFrame or None
		:type columns: NoneType or dict[str, list[str]]
		:type rows: NoneType or dict[str, list[int]]
		"""
		self._label = label
		if _parent is None:
			self._parent = None
			self._graph = None
			if isinstance(data, Mosaic):
				self._original_data = data.original_data
				self._column_groups = columns or data._column_groups.copy()
				self._row_groups = rows or data._row_groups.copy()

			else:
				self._original_data = data
				self._column_groups = columns
				self._row_groups = rows
			self._mosaic_list = []

		else:
			self._parent = _parent
			if data is not None:
				raise ValueError('data should be None when a parent is available!')
			self._original_data = self.parent._original_data
			self._column_groups = columns or self.parent._column_groups.copy()
			self._row_groups = rows or self.parent._row_groups.copy()
			self._graph = self.parent.graph
			self._mosaic_list = None

		if self._row_groups is None:
			self._tile_rows = {'': TileRow(
				mosaic=self, rows=None, label=None, column_groups=self._column_groups
			)}
		else:
			self._tile_rows = {
				label: TileRow(mosaic=self, rows=row_group, label=label, column_groups=self._column_groups)
				for label, row_group in self._row_groups.items()
			}

		self._id = len(self.mosaic_list)
		self._mosaic_list.append(self.label)
		self.graph.add_node(name=str(self._id), label=self.label)
		if self._parent is not None:
			self.graph.connect(start=str(self.parent._id), end=str(self._id))

	_STATE_ATTRIBUTES = ['_original_data', '_column_groups', '_row_groups', '_tile_rows', '_graph', '_mosaic_list', '_parent', '_label']

	@property
	def graph(self):
		"""
		:rtype: Graph
		"""
		return self._graph

	def __getstate__(self):
		return {key: getattr(self, key) for key in self._STATE_ATTRIBUTES}

	def __setstate__(self, state):
		for key, value in state.items():
			setattr(self, key, value)
		self.original_data = self._original_data

	@property
	def label(self):
		"""
		:rtype: str
		"""
		return self._label or f'{self.row_names} \\ {self.column_names}'

	@property
	def mosaic_list(self):
		"""
		:rtype: list[str]
		"""
		if self._parent is None:
			return self._mosaic_list
		else:
			return self.parent.mosaic_list

	@property
	def original_data(self):
		"""
		:rtype: DataFrame
		"""
		if self._parent is None:
			return self._original_data
		else:
			return self.parent.original_data

	@property
	def parent(self):
		"""
		:rtype: NoneType or Mosaic
		"""
		return self._parent

	@original_data.setter
	def original_data(self, original_data):
		if self._parent is None:
			self._original_data = original_data
			for tile_row in self._tile_rows.values():
				tile_row.original_data = original_data
		else:
			raise RuntimeError('cannot set original_data for a child Mosaic')


	def __getitem__(self, item):
		"""
		:type item: str or list[str]
		:rtype: Mosaic
		"""
		if not isinstance(item, tuple):
			if len(self._tile_rows) == 1:
				item = item or ''
			if item in self.row_names:
				return self.get(rows=item)
			elif item in self.column_names:
				return self.get(columns=item)
		elif isinstance(item, tuple):
			if len(item) != 2:
				raise ValueError('item cannot be a tuple larger than 2 in length')
			row, column = item
			return self.get(rows=row, columns=column)

	def represent_data(self, max_columns=None, max_rows=None):
		"""
		:type max_columns: NoneType or int
		:type max_rows: NoneType or int
		:rtype: DataFrame
		"""
		return concat(
			[
				tile_row.represent_data(max_columns=max_columns, max_rows=max_rows)
				for tile_row in self._tile_rows.values()
			],
			axis=0
		)

	def display(self, p=None, max_columns=None, max_rows=None):
		try:
			from IPython.core.display import display
			display(self.represent_data(max_columns=max_columns, max_rows=max_rows))
		except ImportError:
			if p is not None:
				p.pretty(self.represent_data(max_columns=max_columns, max_rows=max_rows))
			else:
				print(self.represent_data(max_columns=max_columns, max_rows=max_rows))

	def _repr_pretty_(self, p, cycle):
		if cycle:
			p.text('Mosaic')
		else:
			self.display(p=p)

	@property
	def num_rows(self):
		num_rows = 0
		for row in self._tile_rows.values():
			num_rows += row.num_rows
		return num_rows

	@property
	def num_columns(self):
		first_key = list(self._tile_rows.keys())[0]
		return self._tile_rows[first_key].num_columns

	def split(self, row_name=None, column_name=None, rows=None, columns=None):
		"""
		:type row_name: str
		:type column_name: str
		:type rows: dict[str, dict[int]]
		:type columns: dict[str, dict[str]]
		:rtype: Mosaic
		"""
		if column_name is not None:
			new_column_groups = {}
			for key, value in self._column_groups.items():
				if key == column_name:
					for subkey, subvalue in columns.items():
						new_column_groups[subkey] = subvalue
				else:
					new_column_groups[key] = value
		else:
			new_column_groups = self._column_groups.copy()

		if row_name is not None:
			new_row_groups = {}
			for key, value in self._row_groups.items():
				if key == row_name:
					for subkey, subvalue in rows.items():
						new_row_groups[subkey] = subvalue
				else:
					new_row_groups[key] = value
		else:
			new_row_groups = self._row_groups.copy()

		return self.__class__(data=self._original_data, columns=new_column_groups, rows=new_row_groups)

	@property
	def rows(self):
		"""
		:rtype: list[TileRow]
		"""
		return [row for row_group in self._row_groups.values() for row in row_group]

	@property
	def row_names(self):
		"""
		:rtype: list[str]
		"""
		return list(self._row_groups.keys())

	@property
	def columns(self):
		"""
		:type: list[str]
		"""
		return [column for column_group in self._column_groups.values() for column in column_group]

	@property
	def column_names(self):
		"""
		:rtype: list[str]
		"""
		return list(self._column_groups.keys())

	@property
	def data(self):
		"""
		:rtype: DataFrame
		"""
		return self._original_data.iloc[self.rows][self.columns]

	def get(self, rows=None, columns=None):
		"""
		:type rows: NoneType or list[str] or str
		:type columns: NoneType or list[str] or str
		:rtype: Mosaic
		"""
		if isinstance(rows, str):
			rows = [rows]
		if isinstance(columns, str):
			columns = [columns]

		if rows is None and columns is None:
			return Mosaic(
				data=None, _parent=self, rows=self._row_groups.copy(), columns=self._column_groups.copy()
			)
		elif rows is None:
			return Mosaic(
				data=None, _parent=self, rows=self._row_groups.copy(),
				columns={key: column_group for key, column_group in self._column_groups.items() if key in columns}
			)
		elif columns is None:
			return Mosaic(
				data=None, _parent=self, columns=self._column_groups.copy(),
				rows={key: row_group for key, row_group in self._row_groups.items() if key in rows}
			)
		else:
			return Mosaic(
				data=None, _parent=self,
				columns={key: column_group for key, column_group in self._column_groups.items() if key in columns},
				rows={key: row_group for key, row_group in self._row_groups.items() if key in rows}
			)

	def rename_row(self, old_key, new_key):
		new_row_groups = {}
		new_tile_rows = {}
		for key, row_group in self._row_groups.items():
			if key == old_key:
				new_row_groups[new_key] = row_group
				new_tile_rows[new_key] = self._tile_rows[old_key]
				if new_tile_rows[new_key]._label == old_key:
					new_tile_rows[new_key]._label = new_key
			else:
				new_row_groups[key] = row_group
				new_tile_rows[key] = self._tile_rows[key]
		self._row_groups = new_row_groups
		self._tile_rows = new_tile_rows

	def rename_column(self, old_key, new_key):
		new_column_groups = {}
		for key, column_group in self._column_groups.values():
			if key == old_key:
				new_column_groups[new_key] = column_group
			else:
				new_column_groups[key] = column_group
		self._column_groups = new_column_groups
		for tile_row in self._tile_rows.values():
			tile_row.rename(old_key, new_key)
