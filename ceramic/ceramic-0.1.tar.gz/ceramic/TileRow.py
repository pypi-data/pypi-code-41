from pandas import DataFrame, concat
from .Tile import Tile


class TileRow:
	def __init__(self, mosaic, rows, label, column_groups=None):
		self._column_groups = column_groups
		self._mosaic = mosaic

		if rows is None:
			self._rows = list(range(len(self.original_data)))
		else:
			non_existing_rows = [row for row in rows if row < 0 or row > self.original_data.shape[0]]
			if len(non_existing_rows) > 0:
				raise KeyError(f'rows {non_existing_rows} do not exist in the data!')
			self._rows = list(rows)

		self._label = label

		if column_groups is None:
			self._tiles = {'': Tile(tile_row=self, rows=self._rows)}
		else:
			self._tiles = {
				column_label: Tile(
					tile_row=self,
					columns=column_group, column_label=column_label,
					rows=rows
				)
				for column_label, column_group in column_groups.items()
			}

	_STATE_ATTRIBUTES = ['_column_groups', '_label', '_tiles']

	def __getstate__(self):
		return {key: getattr(self, key) for key in self._STATE_ATTRIBUTES}

	def __setstate__(self, state):
		for key, value in state.items():
			setattr(self, key, value)

	@property
	def original_data(self):
		"""
		:rtype: DataFrame
		"""
		return self._mosaic.original_data

	@property
	def rows(self):
		return self._rows

	@property
	def columns(self):
		return [column for column_group in self._column_groups.values() for column in column_group]

	@property
	def data(self):
		"""
		:rtype: DataFrame
		"""
		return self.original_data.iloc[self.rows][self.columns]

	@property
	def num_rows(self):
		first_key = list(self._tiles.keys())[0]
		return self._tiles[first_key].num_rows

	@property
	def num_columns(self):
		num_columns = 0
		for tile in self._tiles.values():
			num_columns += tile.num_columns
		return num_columns

	def get(self, columns=None):
		"""
		:type columns: NoneType or list[str] or str
		:rtype: Mosaic
		"""
		if isinstance(columns, str):
			columns = [columns]

		if columns is None:
			return TileRow(
				mosaic=self._mosaic, column_groups=self._column_groups.copy(), label=self._label, rows=self._rows
			)
		else:
			return TileRow(
				mosaic=self._mosaic,
				column_groups={
					key: column_group for key, column_group in self._column_groups.items() if key in columns
				},
				label=self._label, rows=self._rows
			)

	def __getitem__(self, item):
		"""
		:type item: str or list[str]
		:rtype: Tile or TileRow
		"""
		if len(self._tiles) == 1:
			item = item or ''
		if isinstance(item, str):
			return self._tiles[item]
		else:
			return self.get(columns=item)

	def represent_data(self, max_columns=None, max_rows=None):
		"""
		:type max_columns: NoneType or int
		:type max_rows: NoneType or int
		:rtype: DataFrame
		"""
		if self._label is None:
			return concat(
				[tile.represent_data(max_rows=max_rows, max_columns=max_columns) for tile in self._tiles.values()],
				axis=1,
			)
		else:
			return concat(
				[concat(
						[
							tile.represent_data(max_rows=max_rows, max_columns=max_columns)
							for tile in self._tiles.values()
						],
						axis=1,
				)],
				axis=0, keys=[self._label]
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
			p.text('TileRow')
		else:
			self.display(p=p)

	def split(self, rows=None):
		"""
		:type rows: dict[str, list[int]]
		:rtype: dict[str, TileRow]
		"""
		if rows is None:
			return {self._label: self}
		else:
			return {
				row_label: TileRow(
					mosaic=self._mosaic, rows=row_group, label=row_label, column_groups=self._column_groups
				)
				for row_label, row_group in rows.items()
			}

	def rename(self, old_key, new_key):
		new_tiles = {}
		for key, tile in self._tiles.items():
			if key == old_key:
				new_tiles[new_key] = tile
			else:
				new_tiles[key] = tile
		self._tiles = new_tiles
