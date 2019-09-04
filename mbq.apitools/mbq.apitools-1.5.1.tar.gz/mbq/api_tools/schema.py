from copy import copy

from marshmallow import Schema as MarshmallowSchema
from marshmallow import ValidationError as MarshmallowValidationError
from marshmallow import post_load, pre_load

from . import exceptions, fields, settings, utils


# Responses
class Pagination(utils.Immutable):
    """Immutable pagination query parameters."""

    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = settings.project_settings.DEFAULT_PAGE_SIZE


class Params(utils.Immutable):
    """Immutable request query parameters."""

    def __init__(self, **kwargs):
        pagination_data = {}

        if "page" in kwargs and "page_size" in kwargs:
            pagination_data["page"] = kwargs.pop("page", None)
            pagination_data["page_size"] = kwargs.pop("page_size", None)

        self.pagination = Pagination(**pagination_data) if pagination_data else None
        super().__init__(**kwargs)


class Payload(utils.Immutable):
    """Immutable payload data."""


def generate_schema(schema_class, spec):
    spec = copy(spec)
    spec["original_schema_class"] = schema_class
    return type("GeneratedSchema", (schema_class,), spec)


def make_param_schema(spec):
    return generate_schema(ParamSchema, spec)()


class Schema(MarshmallowSchema):
    """."""

    def __init__(self, unknown=None, **kwargs):
        allowed_kwargs = ("many",)
        filtered_kwargs = {
            kwarg: value for kwarg, value in kwargs.items() if kwarg in allowed_kwargs
        }
        super().__init__(unknown=unknown, **filtered_kwargs)

    def load(self, data):
        """Overwrite any `ValidationError`s that may have been risen throughout the load
        process and re-raise it as our own custom error.

        :param dict data: The data that will get deserialized
        :rtype utils.Immutable
        :returns An immutable class with the query params
        """
        try:
            return super().load(data)
        except MarshmallowValidationError as err:
            raise exceptions.ValidationError(err)

    @pre_load
    def call_pre_load_processes(self, data, *args, **kwargs):
        self._generate_nested_fields()
        return self.pre_process_data(data)

    @post_load
    def set_full_result(self, result, *args, **kwargs):
        return self.output_cls(**result)

    def pre_process_data(self, data):
        """To be overridden by subclasses."""
        return data

    def _generate_nested_fields(self):
        for _, field_obj in self.fields.items():
            if isinstance(field_obj, fields.Nested) and field_obj.needs_schema():
                nested = generate_schema(self.original_schema_class, field_obj.fields)()
                field_obj.bind_schema(nested)


class ParamSchema(Schema):
    """Custom param schema to automatically parse query params from a request
        whilst enabling all of the validation features available in marshmallow.

        Example usage::

        .. code-block:: python
            class QueryParam(ParamSchema):
                order_ids = ListParam(StringParam(), param_name='ids')
                company = StringParam(param_name='company_id')

                @validates(company)
                def validate_company_id(id):
                    if not id:
                        raise ValidationError('The company id cannot be empty')

            order_query_params = QueryParam()
            data = order_query_params.load(request)
            data # {'order_ids': [...], 'company': '..'}
    """

    output_cls = Params

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def pre_process_data(self, data):
        return self._transform_from_querydict(data)

    def _transform_from_querydict(self, data):
        # Fields can be declared with a `param_name` different than the attribute name.
        # Map what the expected param_name is to the field_obj.
        declared_fields = {
            (field_obj.data_key or field): field_obj
            for field, field_obj in self._declared_fields.items()
        }
        transformed = {}

        for key, value in data.items():

            if isinstance(declared_fields.get(key), fields._List):
                value = data.getlist(key)
                # If the param was passed, but no value specified, we get empty strings, which we
                # want to prune.
                value = [x for x in value if x != ""]

                # getlist will return a list containing a single string if the param is given as
                # a comma separated value (ex. 'foo=1,2,3'). We need to split the value in that case.
                if len(value) == 1:
                    value = value[0].split(",")

            # If a param is passed in with no value, drop it.
            if value in ([], ""):
                continue

            transformed[key] = value

        return transformed


class PayloadSchema(Schema):

    output_cls = Payload
