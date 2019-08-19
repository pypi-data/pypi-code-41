from marshmallow import Schema, fields, validates_schema, ValidationError

class UsageEventMode(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if not value:
            return ''
        return str(value).lower()

class EventMetricSchema(Schema):
    account_id = fields.Str(empty=False, required=True)
    sub_account_id = fields.Str(empty=False, required=False)
    metadata = fields.Dict()
    metric_name = fields.Str(empty=False, required=True)
    metric_value = fields.Int(empty=False, required=True)
    metric_resolution = fields.Str(empty=False, required=True)
    product = fields.Str(empty=False, required=True)


class UsageEventSchema(Schema):
    date_submitted = fields.DateTime(required=False)
    event_metrics = fields.Nested(EventMetricSchema, many=True, required=False)
    mode = UsageEventMode(empty=False, required=True)
    transaction_id = fields.Str(empty=False, required=False)

    @validates_schema
    def validate_mode(self, data, **kwargs):
        valid_modes = [
            'insert',
            'upsert',
        ]
        if 'mode' in data and data['mode'] in valid_modes:
            return

        error_msg = "UsageEvent.mode value `{}` not valid, must be one of {}" \
            .format(data['mode'], ', '.join(valid_modes))
        raise ValidationError(error_msg, 'mode')
