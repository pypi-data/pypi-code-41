from typing import List, Optional, Dict, Any, Union, Callable

from dateutil.parser import parse as from_iso

from aurora_connector.helpers.Exceptions import AuroraParameterException, AuroraDatabaseException


DATATYPE_MAPPING = {
    "VARCHAR": str,
    "CHAR": str,
    "BINARY": bytes,
    "VARBINARY": bytes,
    "TINYBLOB": bytes,
    "TINYTEXT": str,
    "TEXT": str,
    "BLOB": bytes,
    "MEDIUMTEXT": str,
    "MEDIUMBLOB": str,
    "LONGTEXT": str,
    "LONGBLOB": str,
    "BIT": bytes,
    "TINYINT": int,
    "BOOL": bool,
    "BOOLEAN": bool,
    "SMALLINT": int,
    "MEDIUMINT": int,
    "INT": int,
    "INTEGER": int,
    "BIGINT": int,
    "FLOAT": float,
    "DOUBLE": float,
    "DECIMAL": float,
    "DEC": float,
    "DATETIME": from_iso
}


def format_field(field: Dict[str, Any]) -> Any:
    """
    Returns the value of the field dictionary returned by the Data API.

    The field dictionary has the following structure:
        field = {
            value_name: value
        },
        where value_name in {"stringValue", "blobValue", ...}

    :param field: (dict)
    :return: (Any)
    """

    datatype_identifier, value = list(field.items())[0]

    if datatype_identifier == "blobValue":
        return bytes(value)

    if datatype_identifier == "booleanValue":
        return bool(value)

    if datatype_identifier == "isNull":
        if value:
            return None

    if datatype_identifier == "longValue":
        return int(value)

    if datatype_identifier == "stringValue":
        return str(value)

    raise AuroraDatabaseException({
        "message": "Unsupported query result field datatype.",
        "field_value": value,
        "supported_types": [
            bytes, bool, float, int, str, None
        ]
    })


def cast_field(field_value: Any, column_type: Callable) -> Any:
    """
    Returns the casted field value according to the DATATYPE_MAPPING above

    :param field_value: value of the field (Any)
    :param column_type: class constructor / function that casts the datatype to the correct type (Callable)
    :return: (Any)
    """

    if field_value is None:
        return field_value

    return column_type(field_value)


def format_record(record: List[Dict[str, Any]], column_types: List[Callable]) -> List[Any]:
    """
    Returns the formatted record with correct typing.

    :param record: A list with the following format:
        record = [
            {
                value_name: value
            },
            .
            .
            .
        ]
        where value_name = "stringValue", "blobValue", etc
        (See format_value for more information)
    :param column_types: A list of datatype constructors where the constructor stored at position i
                         relates to the datatype in position i stored in the record. (list)
    :return: (list)
    """

    return [cast_field(format_field(field), column_type) for field, column_type in zip(record, column_types)]


def get_column_type(column_type: str) -> Callable:
    """
    Returns the related data type constructor for the MySQL database with name :param column_type:

    :param column_type: Column type name. e.g. VARCHAR, etc (string)
    :return: (callable)
    """

    if column_type not in DATATYPE_MAPPING:
        raise AuroraDatabaseException({
            "message": "Unsupported column type in result set.",
            "column_type": column_type
        })

    return DATATYPE_MAPPING.get(column_type)


def get_column_types(column_metadata: List[Dict]) -> List[Callable]:
    """
    Parses column_metadata to extract the column types.
    Returns a list of callables, where each callable is the data type constructor for the related column type.
    This allows us to parse column types such as DATETIME which aren't supported by the data api

    :param column_metadata: The columnMetadata returned from the data API (list)
    :return: (list)
    """

    return [
        get_column_type(column.get("typeName")) for column in column_metadata
    ]


def format_response(response: Dict) -> List[List]:
    """

    :param response: Response dictionary from data api for a query.
    :return: (list)
    """

    column_types = get_column_types(response.get("columnMetadata"))
    records = response.get("records")

    return [format_record(record, column_types) for record in records]


def format_value(value: Any) -> Dict[str, Any]:
    """
    Returns value of an sql parameter according to the data api requirements.

    :param value: value of parameter (Any)
    :return: (dict)
    """

    if isinstance(value, bytes):
        return {"blobValue": value}

    if isinstance(value, bool):
        return {"booleanValue": value}

    if isinstance(value, float):
        return {"doubleValue": value}

    if value is None:
        return {"isNull": True}

    if isinstance(value, int):
        return {"longValue": value}

    if isinstance(value, str):
        return {"stringValue": value}

    raise AuroraParameterException({
        "message": "Unsupported parameter datatype.",
        "parameter_value": value,
        "supported_types": [
            bytes, bool, float, int, str, None
        ]
    })


def format_sql_parameters(sql_parameters: Dict[str, Any]) -> List[Dict[str, Union[str, Dict[str, Any]]]]:
    """
    Formats the sql parameters according to the data api requirements.

    :param sql_parameters: A dictionary with the following format:
        sql_parameters = {
            parameter_name: value,
            .
            .
            .
        }
    :return: (list)
    """

    return [
        {"name": name, "value": format_value(value)} for name, value in sql_parameters.items()
    ]


def fetch_one(result_set: List[List]) -> Optional[List]:
    """
    Returns the first record returned from a query.
    If the result set is empty then None is returned

    :param result_set: a list of records returned from AuroraDatabase.query (list)
    :return: (list|None)
    """

    return result_set[0] if result_set else None
