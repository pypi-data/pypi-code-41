"""
This file is part of the MerchantAPI package.

(c) Miva Inc <https://www.miva.com/>

For the full copyright and license information, please view the LICENSE
file that was distributed with self source code.

$Id: listquery.py 77682 2019-08-29 23:21:44Z gidriss $
"""

from merchantapi.abstract import Request
from merchantapi.abstract import Response
from merchantapi.abstract import Client

"""
ListQueryRequest
"""


class ListQueryRequest(Request):
	SORT_ASCENDING = 'asc'
	SORT_DESCENDING = 'desc'

	available_on_demand_columns = []
	available_custom_filters = {}
	available_sort_fields = []
	available_search_fields = []

	def __init__(self, client: Client = None):
		"""
		ListQueryRequest Constructor

		:param client: Client|None
		"""
		super().__init__(client)
		self.sort = None
		self.offset = 0
		self.count = 0
		self.filters = []
		self.expressions = []
		self.on_demand_columns = []
		self.custom_filters = []

	def get_sort(self) -> str:
		"""
		Get the sorting field.

		:returns: str
		"""

		return self.sort

	def set_sort(self, field: str, direction: str = SORT_ASCENDING) -> 'ListQueryRequest':
		"""
		Set the sorting field.

		:param field: str
		:param direction: str
		:returns: ListQueryRequest
		"""

		direction = direction.strip().lower()

		if direction != ListQueryRequest.SORT_ASCENDING and direction != ListQueryRequest.SORT_DESCENDING:
			direction = ListQueryRequest.SORT_ASCENDING
		if direction == ListQueryRequest.SORT_DESCENDING and field[0] != '-':
			field = '-' + field

		self.sort = field

		return self

	def get_available_sort_fields(self) -> list:
		"""
		Get the available sorting fields for the request.

		@returns: list
		"""

		return self.available_sort_fields

	def get_offset(self) -> int:
		"""
		Get the record offset.

		:returns: int
		"""

		return self.offset

	def set_offset(self, offset: int) -> 'ListQueryRequest':
		"""
		Set the record offset.

		:param offset: int
		:returns: ListQueryRequest
		"""

		self.offset = offset
		return self

	def get_count(self) -> int:
		"""
		Get the maximum records to request.

		:returns: int
		"""

		return self.count

	def set_count(self, count: int) -> 'ListQueryRequest':
		"""
		Set the maximum records to request.

		:param count: int
		:returns: ListQueryRequest
		"""

		self.count = count
		return self

	def get_available_search_fields(self) -> list:
		"""
		Get the available search fields for the request.

		:returns: list
		"""

		return self.available_search_fields

	def add_on_demand_column(self, column: str) -> 'ListQueryRequest':
		"""
		Add an on demand column to the request.

		:param column: str
		:returns: ListQueryRequest
		:raises Exception:
		"""
		if column is str:
			column = column.lower()

		if ':' not in column:
			if len(self.available_on_demand_columns) and column not in self.available_on_demand_columns:
				available = ", ".join(self.available_on_demand_columns)
				raise Exception('Invalid Column %s. Available on demand columns are %s' % (column, available))

		if column not in self.on_demand_columns:
			self.on_demand_columns.append(column)

		return self

	def remove_on_demand_column(self, column: str) -> 'ListQueryRequest':
		"""
		Remove an on demand column from the request.

		:param column: str
		:returns: ListQueryRequest
		"""

		if len(self.on_demand_columns):
			for i, col in self.on_demand_columns:
				if col == column:
					del self.on_demand_columns[i]
		return self

	def set_on_demand_columns(self, columns: list) -> 'ListQueryRequest':
		"""
		Set the on demand columns to fetch.

		:param: list
		:returns: ListQueryRequest
		"""

		self.on_demand_columns = []
		for e in columns:
			self.add_on_demand_column(e)
		return self

	def get_on_demand_columns(self) -> list:
		"""
		Get the on demand columns to fetch.

		:returns: list
		"""

		return self.on_demand_columns

	def get_available_on_demand_columns(self) -> list:
		"""
		Get the available on demand columns for the request.

		:returns: list
		"""

		return self.available_on_demand_columns

	def get_custom_filters(self) -> list:
		"""
		Get the custom filters to apply.

		:returns: list
		"""

		return self.custom_filters

	def get_available_custom_filters(self) -> dict:
		"""
		Get the available custom filters for the request.

		:returns: dict
		"""

		return self.available_custom_filters

	def set_filters(self, filters: (list, 'FilterExpression')) -> 'ListQueryRequest':
		"""
		Set the search filters to apply to the request.

		:param filters: list|FilterExpression
		:raises Exception:
		:returns: ListQueryRequest
		"""

		if not isinstance(filters, list) and not isinstance(filters, FilterExpression):
			raise Exception('Expecting an array of instance of FilterExpression')

		self.filters = filters

		return self

	def get_filters(self) -> (list, 'FilterExpression'):
		"""
		Get the search filters to apply to the request.

		:returns: list|FilterExpression
		"""

		return self.filters

	def set_custom_filter(self, name: str, value) -> 'ListQueryRequest':
		"""
		Set a custom filter supported by the request.

		:param name: str
		:param value: mixed
		:returns: ListQueryRequest
		:raises Exception:
		"""

		if name not in self.available_custom_filters:
			raise Exception('Invalid custom filter %s. Available filters are %s' %
							(name, ", ".join(self.available_custom_filters)))

		if isinstance(self.available_custom_filters[name], list):
			if value not in self.available_custom_filters[name]:
				raise Exception('Invalid custom filter choice for %s. Available choices are %s' %
								(name, ", ".join(self.available_custom_filters[name])))
		else:
			if self.available_custom_filters[name] is 'str':
				if not isinstance(value, str):
					raise Exception('Expected str but got %s' % value.__class__)
			elif self.available_custom_filters[name] is 'int':
				if not isinstance(value, int):
					raise Exception('Expected int but got %s' % value.__class__)
			elif self.available_custom_filters[name] is 'float':
				if not isinstance(value, float):
					raise Exception('Expected float but got %s' % value.__class__)
			elif self.available_custom_filters[name] is 'bool':
				if not isinstance(value, bool):
					raise Exception('Expected bool but got %s' % value.__class__)
			else:
				raise Exception('Invalid value type for %s, expected %s' % (name, self.available_custom_filters[name]))

		for cf in self.custom_filters:
			if cf['name'] == name:
				cf['value'] = value
				return self

		self.custom_filters.append({
			"name": name,
			"value": value
		})

		return self

	def remove_custom_filter(self, name) -> 'ListQueryRequest':
		"""
		Remove a custom filter applied to the request.

		:param name: str
		:returns: ListQueryRequest
		"""

		for i, cf in enumerate(self.custom_filters, 0):
			if cf['name'] == name:
				del self.custom_filters[i]
				break

		return self

	def filter_expression(self):
		"""
		Creates a new FilterExpression object in the context of the request.
		:returns: FilterExpression
		"""

		return FilterExpression(self)

	def create_response(self, data) -> 'ListQueryResponse':
		"""
		Creates a ListQueryResponse from an api response

		:returns: ListQueryResponse
		"""

		return ListQueryResponse(self, data)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:returns: dict
		"""

		data = super().to_dict()

		data.update({
			'Sort': self.get_sort(),
			'Offset': self.get_offset(),
			'Count': self.get_count(),
			'Filter': []
		})

		if isinstance(self.filters, FilterExpression):
			data['Filter'] = self.filters.to_list()
		elif isinstance(self.filters, list):
			data['Filter'] = self.filters

		if len(self.on_demand_columns):
			data['Filter'].append({
				'name': 'ondemandcolumns',
				'value': self.on_demand_columns
			})

		for cf in self.custom_filters:
			data['Filter'].append(cf)

		return data


"""
ListQueryResponse
"""


class ListQueryResponse(Response):
	def __init__(self, request: ListQueryRequest, data: dict):
		"""
		ListQueryResponse Constructor

		:param request: ListQueryRequest
		:param data: dict
		"""
		super().__init__(request, data)

	def get_total_count(self) -> int:
		"""
		Get the total count of returned records

		:return: int
		"""

		return self.data['data']['total_count'] if 'data' in self.data and 'total_count' in self.data['data'] else 0

	def get_start_offset(self) -> int:
		"""
		Get the starting offset of the result set

		:return:
		"""

		return self.data['data']['start_offset'] if 'data' in self.data and 'start_offset' in self.data['data'] else 0


"""
FilterExpressionEntry
"""


class FilterExpressionEntry:
	def __init__(self, left, operator, right, search='search'):
		"""
		FilterExpressionEntry Constructor.

		:param left: str
		:param operator: str
		:param right: str
		:param search: str
		"""

		self.left = left
		self.operator = operator
		self.right = right
		self.search = search

	def get_left(self) -> str:
		"""
		Get the left side of the expression.

		:returns: str
		"""

		return self.left

	def set_left(self, left) -> 'FilterExpressionEntry':
		"""
		Set the left side of the comparison.

		:param left: str
		:returns: FilterExpressionEntry
		"""

		self.left = left
		return self

	def get_operator(self) -> str:
		"""
		Get the expression operator.

		:returns: str
		"""

		return self.operator

	def set_operator(self, operator) -> 'FilterExpressionEntry':
		"""
		Set the expression operator.

		:param operator: str
		:returns: FilterExpressionEntry
		"""

		self.operator = operator
		return self

	def get_right(self) -> str:
		"""
		Get the right side of the expression.

		:return: str
		"""

		return self.right

	def set_right(self, right) -> 'FilterExpressionEntry':
		"""
		Set the right side of the expression.

		:param right: str
		:return: FilterExpressionEntry
		"""

		self.right = right
		return self


"""
Filter Expresion

:see: https://docs.miva.com/json-api/list-load-query-overview#filter-list-parameters
"""


class FilterExpression:
	OPERATOR_EQ = 'EQ'					# Operator: Equals
	OPERATOR_GT = 'GT'					# Operator: Greater Than
	OPERATOR_GE = 'GE'					# Operator: Greater Than or Equal
	OPERATOR_LT = 'LT'					# Operator: Less Than
	OPERATOR_LE = 'LE'					# Operator: Less Than or Equal
	OPERATOR_CO = 'CO'					# Operator: Contains
	OPERATOR_NC = 'NC'					# Operator: Does Not Contain
	OPERATOR_LIKE = 'LIKE'				# Operator: Like
	OPERATOR_NOTLIKE = 'NOTLIKE'		# Operator: Not Like
	OPERATOR_NE = 'NE'					# Operator: Not Equal
	OPERATOR_TRUE = 'TRUE'       		# Operator: True
	OPERATOR_FALSE = 'FALSE'      		# Operator: False
	OPERATOR_NULL = 'NULL'       		# Operator: Is Null
	OPERATOR_IN = 'IN'         			# Operator: In Set (comma separated list)
	OPERATOR_NOT_IN = 'NOT_IN'     		# Operator: Not In Set (comma separated list)
	OPERATOR_SUBWHERE = 'SUBWHERE'   	# Operator: SUBWHERE

	VALID_OPERATORS = [
		OPERATOR_EQ,
		OPERATOR_GT,
		OPERATOR_GE,
		OPERATOR_LT,
		OPERATOR_LE,
		OPERATOR_CO,
		OPERATOR_NC,
		OPERATOR_LIKE,
		OPERATOR_NOTLIKE,
		OPERATOR_NE,
		OPERATOR_TRUE,
		OPERATOR_FALSE,
		OPERATOR_NULL,
		OPERATOR_IN,
		OPERATOR_NOT_IN,
		OPERATOR_SUBWHERE
	]

	# Search Filter Constants
	FILTER_SEARCH = 'search'
	FILTER_SEARCH_AND = 'search_AND'
	FILTER_SEARCH_OR = 'search_OR'

	VALID_FILTERS = [
		FILTER_SEARCH,
		FILTER_SEARCH_AND,
		FILTER_SEARCH_OR
	]

	def __init__(self, request: 'ListQueryRequest' = None):
		"""
		FilterExpression Constructor.

		:param request: Request|None
		"""

		self.request = request
		self.parent = None
		self.expressions = []

	def get_parent(self) -> ('FilterExpression', None):
		"""
		Get the parent expression.

		:returns: FilterExpression|None
		"""

		return self.parent

	def set_parent(self, parent=None) -> 'FilterExpression':
		"""
		Set the parent expression.

		:param parent: FilterExpression|None
		:return: FilterExpression
		"""

		self.parent = parent
		return self

	def is_child(self) -> bool:
		"""
		Check if self expression is a child of another.

		:return: bool
		"""

		return self.parent is not None

	def child_depth(self) -> int:
		"""
		Get the child depth.

		:return: int
		"""

		i = 0
		parent = self.get_parent()

		while parent:
			parent = parent.get_parent()
			i = i + 1

		return i

	def expr(self) -> 'FilterExpression':
		"""
		Create a new expression instance.

		:return: FilterExpression
		"""

		return FilterExpression(self.request)

	def add(self, field: str, operator, value, filter_type) -> 'FilterExpression':
		"""
		Add a search filter.

		:param field: str
		:param operator: str
		:param value: mixed
		:param filter_type: str
		:return: FilterExpression
		:raises Exception:
		"""

		operator = operator.upper()

		if self.request is not None:
			if field not in self.request.get_available_search_fields():
				raise Exception('Field %s is invalid. Available fields are: %s' %
								(field, ", ".join(self.request.get_available_search_fields())))

		if operator not in FilterExpression.VALID_OPERATORS:
			raise Exception('Operator %s is invalid. Available operators are: %s' %
							(field, ", ".join(FilterExpression.VALID_OPERATORS)))

		if filter_type not in FilterExpression.VALID_FILTERS:
			raise Exception('Filter type %s is invalid. Available search filter types are %s' %
							(field, ", ".join(FilterExpression.VALID_FILTERS)))

		if not len(self.expressions):
			filter_type = FilterExpression.FILTER_SEARCH
		elif len(self.expressions) and filter_type == FilterExpression.FILTER_SEARCH:
			filter_type = FilterExpression.FILTER_SEARCH_OR

		if filter_type in (FilterExpression.FILTER_SEARCH, FilterExpression.FILTER_SEARCH_AND):
			self.expressions.append({
				'type': filter_type,
				'entry': FilterExpressionEntry(field, operator, value, filter_type)
			})
		elif filter_type == FilterExpression.FILTER_SEARCH_OR:
			self.expressions.append({
				'type': filter_type,
				'entry': FilterExpressionEntry(field, operator, value, filter_type)
			})
		else:
			raise Exception('Invalid type %s' % filter_type)

		return self

	def and_x(self, expression) -> 'FilterExpression':
		"""
		Add a AND expression.

		:param expression: FilterExpression
		:return: FilterExpression
		:raises Exception:
		"""

		expression.set_parent(self)

		self.expressions.append({
			'type': FilterExpression.FILTER_SEARCH_AND,
			'entry': expression
		})

		return self

	def or_x(self, expression) -> 'FilterExpression':
		"""
		Add a OR expression.

		:param expression: FilterExpression
		:return: FilterExpression
		:raises Exception:
		"""

		expression.set_parent(self)

		self.expressions.append({
			'type': FilterExpression.FILTER_SEARCH_OR,
			'entry': expression
		})

		return self

	def equal(self, field: str, value: (str, int, float)) -> 'FilterExpression':
		"""
		Add a equal (x EQ y) filter for specified field.

		:param field: str
		:param value: mixed
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_EQ, value, FilterExpression.FILTER_SEARCH)

	def and_equal(self, field: str, value: (str, int, float)) -> 'FilterExpression':
		"""
		Add a equal (AND x EQ y) filter for specified field.

		:param field: str
		:param value: mixed
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_EQ, value, FilterExpression.FILTER_SEARCH_AND)

	def or_equal(self, field: str, value: (str, int, float)) -> 'FilterExpression':
		"""
		Add a equal (OR x EQ y) filter for specified field.

		:param field: str
		:param value: mixed
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_EQ, value, FilterExpression.FILTER_SEARCH_OR)

	def greater_than(self, field: str, value: (int, float)) -> 'FilterExpression':
		"""
		Add a greater than (x GT y) filter for specified field.

		:param field: str
		:param value: int|float
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_GT, value, FilterExpression.FILTER_SEARCH)

	def and_greater_than(self, field: str, value: (int, float)) -> 'FilterExpression':
		"""
		Add a greater than (AND x GT y) filter for specified field.

		:param field: str
		:param value: int|float
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_GT, value, FilterExpression.FILTER_SEARCH_AND)

	def or_greater_than(self, field: str, value: (int, float)) -> 'FilterExpression':
		"""
		Add a greater than (OR x GT y) filter for specified field.

		:param field: str
		:param value: int|float
		:return: FilterExpression
		"""
		return self.add(field, FilterExpression.OPERATOR_GT, value, FilterExpression.FILTER_SEARCH_OR)

	def greater_than_equal(self, field: str, value: (int, float)) -> 'FilterExpression':
		"""
		Add a greater than or equal (x GE y) filter for specified field.

		:param field: str
		:param value: int|float
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_GE, value, FilterExpression.FILTER_SEARCH)

	def and_greater_than_equal(self, field: str, value: (int, float)) -> 'FilterExpression':
		"""
		Add a greater than or equal (AND x GE y) filter for specified field.

		:param field: str
		:param value: int|float
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_GE, value, FilterExpression.FILTER_SEARCH_AND)

	def or_greater_than_equal(self, field: str, value: (int, float)) -> 'FilterExpression':
		"""
		Add a greater than or equal (OR x GE y) filter for specified field.

		:param field: str
		:param value: int|float
		:return:  FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_GE, value, FilterExpression.FILTER_SEARCH_OR)

	def less_than(self, field: str, value: (int, float)) -> 'FilterExpression':
		"""
		Add a less than (x LT y) filter for specified field.
		:param field: str
		:param value: int|float
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_LT, value, FilterExpression.FILTER_SEARCH)

	def and_less_than(self, field: str, value: (int, float)) -> 'FilterExpression':
		"""
		Add a less than (AND x LT y) filter for specified field.

		:param field: str
		:param value: int|float
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_LT, value, FilterExpression.FILTER_SEARCH_AND)

	def or_less_than(self, field: str, value: (int, float)) -> 'FilterExpression':
		"""
		Add a less than (OR x LT y) filter for specified field.

		:param field: str
		:param value: int|float
		:return:  FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_LT, value, FilterExpression.FILTER_SEARCH_OR)

	def less_than_equal(self, field: str, value: (int, float)) -> 'FilterExpression':
		"""
		Add a less than or equal (x LE y) filter for specified field.

		:param field: str
		:param value: int|float
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_LE, value, FilterExpression.FILTER_SEARCH)

	def and_less_than_equal(self, field: str, value: (int, float)) -> 'FilterExpression':
		"""
		Add a less than or equal (AND x LE y) filter for specified field.

		:param field: str
		:param value: int|float
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_LE, value, FilterExpression.FILTER_SEARCH_AND)

	def or_less_than_equal(self, field: str, value: (int, float)) -> 'FilterExpression':
		"""
		Add a less than or equal (OR x LE y) filter for specified field.

		:param field: str
		:param value: int|float
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_LE, value, FilterExpression.FILTER_SEARCH_OR)

	def contains(self, field: str, value: str) -> 'FilterExpression':
		"""
		Add a contains (x CO y) filter for specified field.

		:param field: str
		:param value: str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_CO, value, FilterExpression.FILTER_SEARCH)

	def and_contains(self, field: str, value: str) -> 'FilterExpression':
		"""
		Add a contains (AND x CO y) filter for specified field.

		:param field: str
		:param value: str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_CO, value, FilterExpression.FILTER_SEARCH_AND)

	def or_contains(self, field: str, value: str) -> 'FilterExpression':
		"""
		Add a contains (OR x CO y) filter for specified field.

		:param field: str
		:param value: str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_CO, value, FilterExpression.FILTER_SEARCH_OR)

	def does_not_contain(self, field: str, value: str) -> 'FilterExpression':
		"""
		Add a does not contains (x NC y) filter for specified field.

		:param field: str
		:param value: str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_NC, value, FilterExpression.FILTER_SEARCH)

	def and_does_not_contain(self, field: str, value: str) -> 'FilterExpression':
		"""
		Add a does not contains (AND x NC y) filter for specified field.

		:param field: str
		:param value: str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_NC, value, FilterExpression.FILTER_SEARCH_AND)

	def or_does_not_contain(self, field: str, value: str) -> 'FilterExpression':
		"""
		Add a does not contains (OR x NC y) filter for specified field.

		:param field: str
		:param value: str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_NC, value, FilterExpression.FILTER_SEARCH_OR)

	def like(self, field: str, value: str) -> 'FilterExpression':
		"""
		Add a like (x LIKE y) filter for specified field.

		:param field: str
		:param value: str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_LIKE, value, FilterExpression.FILTER_SEARCH)

	def and_like(self, field: str, value: str) -> 'FilterExpression':
		"""
		Add a like (AND x LIKE y) filter for specified field.

		:param field: str
		:param value: str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_LIKE, value, FilterExpression.FILTER_SEARCH_AND)

	def or_like(self, field: str, value: str) -> 'FilterExpression':
		"""
		Add a like (OR x LIKE y) filter for specified field.

		:param field: str
		:param value: str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_LIKE, value, FilterExpression.FILTER_SEARCH_OR)

	def not_like(self, field: str, value: str) -> 'FilterExpression':
		"""
		Add a not like (x NOTLIKE y) filter for specified field.

		:param field: str
		:param value: str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_NOTLIKE, value, FilterExpression.FILTER_SEARCH)

	def and_not_like(self, field: str, value: str) -> 'FilterExpression':
		"""
		Add a not like (AND x NOTLIKE y) filter for specified field.

		:param field: str
		:param value: str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_NOTLIKE, value, FilterExpression.FILTER_SEARCH_AND)

	def or_not_like(self, field: str, value: str) -> 'FilterExpression':
		"""
		Add a not like (OR x NOTLIKE y) filter for specified field.

		:param field: str
		:param value: str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_NOTLIKE, value, FilterExpression.FILTER_SEARCH_OR)

	def not_equal(self, field: str, value: (str, int, float)) -> 'FilterExpression':
		"""
		Add a not equal (x NE y) filter for specified field.

		:param field: str
		:param value: mixed
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_NE, value, FilterExpression.FILTER_SEARCH)

	def and_not_equal(self, field: str, value: (str, int, float)) -> 'FilterExpression':
		"""
		Add a not equal (AND x NE y) filter for specified field.

		:param field: str
		:param value: mixed
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_NE, value, FilterExpression.FILTER_SEARCH_AND)

	def or_not_equal(self, field: str, value: (str, int, float)) -> 'FilterExpression':
		"""
		Add a not equal (OR x NE y) filter for specified field.

		:param field: str
		:param value: mixed
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_NE, value, FilterExpression.FILTER_SEARCH_OR)

	def is_true(self, field: str) -> 'FilterExpression':
		"""
		Add a true (x == true) filter for specified field.

		:param field: str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_TRUE, None, FilterExpression.FILTER_SEARCH)

	def and_is_true(self, field: str) -> 'FilterExpression':
		"""
		Add a true (AND x == true) filter for specified field.

		:param field: str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_TRUE, None, FilterExpression.FILTER_SEARCH_AND)

	def or_is_true(self, field: str) -> 'FilterExpression':
		"""
		Add a true (OR x == true) filter for specified field.

		:param field: str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_TRUE, None, FilterExpression.FILTER_SEARCH_OR)

	def is_false(self, field: str) -> 'FilterExpression':
		"""
		Add a false (x == false) filter for specified field.

		:param field: str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_FALSE, None, FilterExpression.FILTER_SEARCH)

	def and_is_false(self, field: str) -> 'FilterExpression':
		"""
		Add a false (AND x == false) filter for specified field.

		:param field: str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_FALSE, None, FilterExpression.FILTER_SEARCH_AND)

	def or_is_false(self, field: str) -> 'FilterExpression':
		"""
		Add a false (OR x == false) filter for specified field.

		:param field: str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_FALSE, None, FilterExpression.FILTER_SEARCH_OR)

	def is_null(self, field: str) -> 'FilterExpression':
		"""
		Add a is None (x == None) filter for specified field.

		:param field: str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_NULL, None, FilterExpression.FILTER_SEARCH)

	def and_is_null(self, field: str) -> 'FilterExpression':
		"""
		Add a is None (AND x == None) filter for specified field.

		:param field: str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_NULL, None, FilterExpression.FILTER_SEARCH_AND)

	def or_is_null(self, field: str) -> 'FilterExpression':
		"""
		Add a is None (OR x == None) filter for specified field.

		:param field: str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_NULL, None, FilterExpression.FILTER_SEARCH_OR)

	def is_in(self, field: str, values: (str, list)) -> 'FilterExpression':
		"""
		Add a in (x IN y,z,.. ) filter for specified field.

		:param field: str
		:param values: list|str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_IN, values, FilterExpression.FILTER_SEARCH)

	def and_is_in(self, field: str, values: (str, list)) -> 'FilterExpression':
		"""
		Add a in (AND x IN y,z,.. ) filter for specified field.

		:param field: str
		:param values: list|str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_IN, values, FilterExpression.FILTER_SEARCH_AND)

	def or_is_in(self, field: str, values: (str, list)) -> 'FilterExpression':
		"""
		Add a in (OR x IN y,z,.. ) filter for specified field.

		:param field: str
		:param values: list|str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_IN, values, FilterExpression.FILTER_SEARCH_OR)

	def not_in(self, field: str, values: (str, list)) -> 'FilterExpression':
		"""
		Add a not in (x NOTIN y,z,.. ) filter for specified field.

		:param field: str
		:param values: list|str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_NOT_IN, values, FilterExpression.FILTER_SEARCH)

	def and_not_in(self, field: str, values: (str, list)) -> 'FilterExpression':
		"""
		Add a not in (AND x NOTIN y,z,.. ) filter for specified field.

		:param field: str
		:param values: list|str
		:return: FilterExpression
		"""

		return self.add(field, FilterExpression.OPERATOR_NOT_IN, values, FilterExpression.FILTER_SEARCH_AND)

	def or_not_in(self, field: str, values: (str, list)) -> 'FilterExpression':
		"""
		Add a not in (OR x NOTIN y,z,.. ) filter for specified field.

		:param field: str
		:param values: list|str
		:return: FilterExpression
		"""
		return self.add(field, FilterExpression.OPERATOR_NOT_IN, values, FilterExpression.FILTER_SEARCH_OR)

	def to_list(self) -> list:
		"""
		Reduce the built expression(s) to an array.

		:returns: list
		"""

		ret = []
		for e in self.expressions:
			if isinstance(e['entry'], FilterExpression):
				entry = {
					'name': e['type'],
					'value': e['entry'].to_list()
				}
			elif self.is_child():
				entry = {
					'field': e['type'],
					'operator': FilterExpression.OPERATOR_SUBWHERE,
					'value': [
						{
							'field': e['entry'].get_left(),
							'operator': e['entry'].get_operator(),
							'value': ",".join(e['entry'].get_right()) if isinstance(e['entry'].get_right(), list) else e['entry'].get_right()
						},
					]
				}
			else:
				entry = {
					'name': e['type'],
					'value': [
						{
							'field': e['entry'].get_left(),
							'operator': e['entry'].get_operator(),
							'value': ",".join(e['entry'].get_right()) if isinstance(e['entry'].get_right(), list) else e['entry'].get_right()

						}
					]
				}
			ret.append(entry)
		return ret
