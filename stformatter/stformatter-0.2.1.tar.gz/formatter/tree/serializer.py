from marshmallow import fields, Schema

class BaseNodeDBSerializator(Schema):
    type = fields.String() # Тип объекта строкой
    format_sign = fields.Boolean(allow_none=True) # Признак формата в строке Boolean
    path = fields.String(allow_none=True) # Полный путь до файла
    filename = fields.String(allow_none=True) # Название файла
    line_number = fields.Integer(allow_none=True) # Номер строки
    content = fields.String(allow_none=True) # Содержит исходную строку целиком
