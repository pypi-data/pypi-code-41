from pandas import DataFrame, concat


class Tile:
	def __init__(self, tile_row, columns=None, rows=None, column_label=None, row_label=None):
		"""
		:type data: DataFrame
		:type columns: list[str] or NoneType
		:type rows: list[int] or NoneType
		:type column_label: str or NoneType
		:type row_label: str or NoneType
		"""
		self._tile_row = tile_row


		if columns is None:
			self._columns = list(data.columns)
		else:
			non_existing_columns = [col for col in columns if col not in data.columns]
			if len(non_existing_columns) > 0:
				raise KeyError(f'columns {non_existing_columns} do not exist in the data!')
			self._columns = list(columns)

		if rows is None:
			self._rows = list(range(len(data)))
		else:
			non_existing_rows = [row for row in rows if row < 0 or row > data.shape[0]]
			if len(non_existing_rows) > 0:
				raise KeyError(f'rows {non_existing_rows} do not exist in the data!')
			self._rows = rows

		self._column_label = column_label
		self._row_label = row_label

	@property
	def original_data(self):
		"""
		:rtype: DataFrame
		"""
		return self._tile_row.original_data

	@property
	def data(self):
		"""
		:rtype: DataFrame
		"""
		return self.original_data.iloc[self.rows][self.columns]

	def split(self, columns=None, row_label=None):
		"""
		:type columns: dict[str, list[str]]
		:rtype: dict[str, Tile]
		"""
		row_label = row_label or self._row_label
		if columns is None:
			return {self._column_label: self}
		else:
			return {
				column_label: Tile(
					tile_row=self._tile_row, columns=column_group, rows=self._rows,
					row_label=row_label, column_label=column_label
				)
				for column_label, column_group in columns.items()
			}

	@property
	def columns(self):
		"""
		:rtype: list[str]
		"""
		return self._columns

	@property
	def rows(self):
		"""
		:rtype: list[int]
		"""
		return self._rows

	@property
	def num_rows(self):
		"""
		:rtype: int
		"""
		return len(self._rows)

	@property
	def num_columns(self):
		"""
		:rtype: int
		"""
		return len(self._columns)

	@property
	def shape(self):
		"""
		:rtype: int, int
		"""
		return  self.num_rows, self.num_columns

	def represent_data(self, max_columns=None, max_rows=None):
		"""
		:type max_columns: NoneType or int
		:type max_rows: NoneType or int
		:rtype: DataFrame
		"""
		if max_columns is None:
			columns = self._columns
		else:
			columns = self._columns[:min(self.num_columns, max_columns)]

		if max_rows is None:
			rows = self._rows
		else:
			rows = self._rows[:min(self.num_rows, max_rows)]

		if max_columns == 0 and max_rows == 0:
			data = DataFrame({'': [f'{self.num_rows}x{self.num_columns}']}, index=[''])
		else:
			data = self.original_data.iloc[rows][columns]

		if self._row_label is None and self._column_label is None:
			return data
		elif self._row_label is None:
			return concat([data], axis=1, keys=[self._column_label])
		elif self._column_label is None:
			return concat([data], axis=0, keys=[self._row_label])
		else:
			return concat(
				[concat([data], axis=1, keys=[self._column_label])],
				axis=0, keys=[self._row_label]
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
			p.text('Tile')
		else:
			self.display(p=p)
