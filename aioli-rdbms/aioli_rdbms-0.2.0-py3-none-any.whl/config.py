from aioli.config import PackageConfigSchema, fields, validate


class ConfigSchema(PackageConfigSchema):
    type = fields.String(
        validate=validate.OneOf(["mysql", "postgres"]),
        required=True
    )
    username = fields.String(required=True)
    password = fields.String(required=True)
    host = fields.String(missing="127.0.0.1")
    port = fields.Integer(missing=3306)
    database = fields.String(missing="aioli")
