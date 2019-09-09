import logging

class SQLQueryString:

    PLACEHOLDER_STRING_FIELD = 'PlaceholderString'
    NEEDS_PARSING_FIELD = 'NeedsParsing'
    LITERAL_VALUE_FIELD = 'LiteralValue'

    def __init__(self, raw_query: str, placeholder_data: dict = None):
        self.raw_query: str = raw_query
        self.placeholder_data: list = placeholder_data
        if placeholder_data is not None:
            self.__set_placeholders()
        else:
            self.query_string = raw_query

    def get_query_string(self) -> str:
        return self.query_string

    def __set_placeholders(self) -> None:
        string_replace_map = {placeholder[self.PLACEHOLDER_STRING_FIELD]: self.__get_placeholder_literal(placeholder=placeholder) for placeholder in self.placeholder_data}
        self.query_string = self.raw_query.format(**string_replace_map)

    def __get_placeholder_literal(self, placeholder: dict) -> str:
        if placeholder[SQLQueryString.NEEDS_PARSING_FIELD]:
            parsed_literal = self.__evaluate_placeholder_expression(placeholder_expression=placeholder[SQLQueryString.LITERAL_VALUE_FIELD])
        else:
            parsed_literal = placeholder[SQLQueryString.LITERAL_VALUE_FIELD]
        return parsed_literal

    def __evaluate_placeholder_expression(self, placeholder_expression) -> str:
        evaluated_expression = eval(placeholder_expression)
        return evaluated_expression


class SQLQuerySet:

    QUERY_FOLDER_PATH_FIELD = 'QueryFolderPath'
    QUERY_FILE_NAME_FIELD = 'QueryFileName'
    QUERY_PLACEHOLDERS_FIELD = 'QueryPlaceholders'

    def __init__(self, queries_config):
        self.query_hash = dict()
        self.order_keys: list = None
        self.queries_config = queries_config.copy()
        self.__set_query_index_keys()
        self.logger = logging.getLogger('SQLQuerySet')

    def __set_query_index_keys(self):
        self.order_keys = sorted([int(index) for index in self.queries_config.keys()])

    def fetch_queries(self, root_path: str = None) -> None:
        if root_path is None:
            root_path = './'
        for index, queries_config in self.queries_config.items():
            query_file_path = root_path + queries_config[SQLQuerySet.QUERY_FOLDER_PATH_FIELD] + queries_config[SQLQuerySet.QUERY_FILE_NAME_FIELD]
            with open(query_file_path, 'r') as query_file:
                query_string = query_file.read()
            self.query_hash[index] = query_string

    def build_query_set(self, runtime_placeholder_map: dict = None) -> None:
        for index, QueryConfig in self.queries_config.items():
            raw_query_string = self.query_hash[str(index)]
            placeholder_data = self.__set_runtime_placeholders(runtime_placeholders=runtime_placeholder_map,
                                                               placeholder_hash=QueryConfig[SQLQuerySet.QUERY_PLACEHOLDERS_FIELD])
            query_string = SQLQueryString(raw_query_string, placeholder_data=placeholder_data)
            self.query_hash[str(index)] = query_string.get_query_string()

    def get_query_set(self):
        return self.query_hash

    def __set_runtime_placeholders(self, runtime_placeholders: dict, placeholder_hash: dict) -> dict:
        if runtime_placeholders is None:
            return placeholder_hash
        for placeholder in placeholder_hash:
            if placeholder[SQLQueryString.PLACEHOLDER_STRING_FIELD] in runtime_placeholders.keys() and\
               placeholder[SQLQueryString.LITERAL_VALUE_FIELD] is None:
                placeholder[SQLQueryString.LITERAL_VALUE_FIELD] = runtime_placeholders[placeholder[SQLQueryString.PLACEHOLDER_STRING_FIELD]]
        return placeholder_hash
