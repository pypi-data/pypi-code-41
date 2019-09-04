from decimal import Decimal

from django.http import QueryDict
from django.test import SimpleTestCase

from mbq.api_tools import exceptions, fields, schema


class DefaultKwargTests(SimpleTestCase):
    def test_no_default_means_required(self):
        spec = {"name": fields.String()}
        param_schema = schema.make_param_schema(spec)

        with self.assertRaises(exceptions.ValidationError):
            param_schema.load({})

        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()

        with self.assertRaises(exceptions.ValidationError):
            payload_schema.load({})

    def test_default_omit(self):
        param_schema = schema.make_param_schema(
            {"name": fields.String(default=fields.OMIT)}
        )

        with self.assertRaises(AttributeError):
            param_schema.load({}).name


class IntFieldTests(SimpleTestCase):
    def test_size(self):
        spec = {"age": fields.Int()}
        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()

        payload_schema.load({"age": 1})
        payload_schema.load({"age": 7})

        spec = {"age": fields.Int(min_val=5)}
        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()
        payload_schema.load({"age": 6})
        with self.assertRaises(exceptions.ValidationError):
            payload_schema.load({"age": 1})

        spec = {"age": fields.Int(max_val=10)}
        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()
        payload_schema.load({"age": 7})
        with self.assertRaises(exceptions.ValidationError):
            payload_schema.load({"age": 15})

        spec = {"age": fields.Int(min_val=5, max_val=5)}
        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()
        payload_schema.load({"age": 5})
        with self.assertRaises(exceptions.ValidationError):
            payload_schema.load({"age": 1})
        with self.assertRaises(exceptions.ValidationError):
            payload_schema.load({"age": 6})


class StringFieldTests(SimpleTestCase):
    def test_missing_value(self):
        param_schema = schema.make_param_schema({"name": fields.String(default=None)})
        result = param_schema.load(QueryDict("name="))
        self.assertEqual(result.name, None)

    def test_allow_empty(self):
        payload_schema = schema.generate_schema(
            schema.PayloadSchema, {"name": fields.String()}
        )()

        result = payload_schema.load({"name": "john"})
        self.assertEqual(result.name, "john")

        with self.assertRaises(exceptions.ValidationError):
            payload_schema.load({"name": ""})

        payload_schema = schema.generate_schema(
            schema.PayloadSchema, {"name": fields.String(allow_empty=True)}
        )()
        result = payload_schema.load({"name": ""})
        self.assertEqual(result.name, "")

    def test_length(self):
        spec = {"name": fields.String()}
        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()

        payload_schema.load({"name": "a"})
        payload_schema.load({"name": "abcdefg"})

        spec = {"name": fields.String(min_length=5)}
        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()
        payload_schema.load({"name": "abcdefg"})
        with self.assertRaises(exceptions.ValidationError):
            payload_schema.load({"name": "a"})

        spec = {"name": fields.String(max_length=10)}
        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()
        payload_schema.load({"name": "abcdefg"})
        with self.assertRaises(exceptions.ValidationError):
            payload_schema.load({"name": "abcdefghijklmnop"})

        spec = {"name": fields.String(min_length=5, max_length=5)}
        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()
        payload_schema.load({"name": "abcde"})
        with self.assertRaises(exceptions.ValidationError):
            payload_schema.load({"name": "a"})
        with self.assertRaises(exceptions.ValidationError):
            payload_schema.load({"name": "abcdefg"})

    def test_min_length_with_allow_empty(self):
        spec = {"name": fields.String(min_length=10, allow_empty=True)}
        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()

        payload_schema.load({"name": ""})
        payload_schema.load({"name": "abcdefghiklmnop"})

        with self.assertRaises(exceptions.ValidationError):
            payload_schema.load({"name": "a"})


class EnumFieldTests(SimpleTestCase):
    def test_choices(self):
        spec = {"name": fields.Enum(choices=["foo", "bar"])}
        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()

        payload_schema.load({"name": "foo"})

        with self.assertRaises(exceptions.ValidationError):
            payload_schema.load({"name": "fizz"})


class NestedFieldTest(SimpleTestCase):
    def test_basic_param_schema(self):
        """Test that the params schema is generated correctly."""
        param_schema = schema.make_param_schema(
            {
                "category": fields.Nested(
                    {"id": fields.Int(), "description": fields.String()}
                )
            }
        )

        result = param_schema.load(
            {"category": {"id": 42, "description": "Rocket Coffee"}}
        )
        self.assertEqual(result.category.id, 42)
        self.assertEqual(result.category.description, "Rocket Coffee")

    def test_class_param_schema(self):
        class CategorySchema(schema.ParamSchema):
            id = fields.Int()
            type = fields.String()

        param_schema = schema.make_param_schema(
            {"category": fields.Nested(CategorySchema)}
        )

        result = param_schema.load({"category": {"id": 42, "type": "coffee"}})
        self.assertEqual(result.category.id, 42)
        self.assertEqual(result.category.type, "coffee")

    def test_list_param_schema(self):
        """Test that list param schemas are generated correctly."""
        param_schema = schema.make_param_schema(
            {
                "categories": fields.Nested(
                    {"id": fields.Int(), "description": fields.String()}, many=True
                )
            }
        )

        result = param_schema.load(
            {
                "categories": [
                    {"id": 42, "description": "Rocket Coffee"},
                    {"id": 16, "description": "Chocolate Quasar"},
                ]
            }
        )
        self.assertEqual(result.categories[0].id, 42)
        self.assertEqual(result.categories[1].id, 16)

    def test_payload_params(self):
        """Test that nested params works."""
        schema_spec = {
            "offers": fields.Nested({"id": fields.Int()}, many=True),
            "orders": fields.Nested(
                {"id": fields.Int(), "quotes": fields.Int(many=True)}, many=True
            ),
        }
        payload_schema = schema.generate_schema(schema.PayloadSchema, schema_spec)()
        result = payload_schema.load(
            {
                "offers": [{"id": 1}, {"id": 2}],
                "orders": [{"id": 10, "quotes": [1, 2, 3]}],
            }
        )
        self.assertEqual(result.offers[0].id, 1)
        self.assertEqual(len(result.offers), 2)
        self.assertEqual(result.orders[0].id, 10)
        self.assertEqual(len(result.orders[0].quotes), 3)

    def test_is_required_by_default(self):
        spec = {"nested": fields.Nested({"foo": fields.String()})}
        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()

        with self.assertRaises(exceptions.ValidationError):
            payload_schema.load({})

        spec = {"nested": fields.Nested({"foo": fields.String(many=True)})}
        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()

        with self.assertRaises(exceptions.ValidationError):
            payload_schema.load({})


class DecimalFieldTests(SimpleTestCase):
    def test_max_digits(self):
        param_schema = schema.make_param_schema({"price": fields.Decimal(max_digits=6)})

        with self.assertRaises(exceptions.ValidationError):
            param_schema.load(QueryDict("price=1234560"))

        with self.assertRaises(exceptions.ValidationError):
            param_schema.load(QueryDict("price=123456.0"))

        with self.assertRaises(exceptions.ValidationError):
            param_schema.load(QueryDict("price=12345.60"))

        with self.assertRaises(exceptions.ValidationError):
            param_schema.load(QueryDict("price=0.0000001"))

    def test_size(self):
        spec = {"age": fields.Decimal()}
        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()

        payload_schema.load({"age": 1.1})
        payload_schema.load({"age": 7.1})

        spec = {"age": fields.Decimal(min_val=5.5)}
        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()
        payload_schema.load({"age": 6.2})
        with self.assertRaises(exceptions.ValidationError):
            payload_schema.load({"age": 1.3})

        spec = {"age": fields.Decimal(max_val=10)}
        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()
        payload_schema.load({"age": 7})
        with self.assertRaises(exceptions.ValidationError):
            payload_schema.load({"age": 15})

        spec = {"age": fields.Decimal(min_val=5, max_val=5)}
        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()
        payload_schema.load({"age": 5})
        with self.assertRaises(exceptions.ValidationError):
            payload_schema.load({"age": 1.4})
        with self.assertRaises(exceptions.ValidationError):
            payload_schema.load({"age": 6.2})


class EmailFieldTests(SimpleTestCase):
    def test_required(self):
        spec = {"email": fields.Email()}

        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()

        with self.assertRaises(exceptions.ValidationError):
            payload_schema.load({})


class TransformFieldTests(SimpleTestCase):
    def test_string_transform(self):
        spec = {"zipcode": fields.String(transform=lambda x: x.strip())}

        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()

        data = payload_schema.load({"zipcode": " 07770"})

        self.assertEqual(data.zipcode, "07770")

    def test_decimal_transform(self):
        spec = {"tax": fields.Decimal(transform=lambda x: round(x, 2))}

        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()

        data = payload_schema.load({"tax": 10.125})

        self.assertEqual(data.tax, Decimal("10.12"))

    def test_error_handling(self):
        def transform(val):
            raise ValueError("too old!")

        spec = {"age": fields.Int(transform=transform)}

        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()

        with self.assertRaises(exceptions.ValidationError):
            payload_schema.load({"age": 100})

    def test_trasnform_with_validation(self):
        spec = {"zipcode": fields.String(transform=lambda x: x.strip(), max_length=4)}

        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()

        with self.assertRaises(exceptions.ValidationError):
            payload_schema.load({"zipcode": " 07770"})

        spec = {"zipcode": fields.String(transform=lambda x: x.strip(), max_length=5)}

        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()

        data = payload_schema.load({"zipcode": " 07770"})

        self.assertEqual(data.zipcode, "07770")

    def test_transform_with_many(self):
        spec = {"zipcode": fields.String(transform=lambda x: x.strip(), many=True)}

        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()

        data = payload_schema.load({"zipcode": [" 07770", "1123", "123 "]})

        self.assertEqual(data.zipcode, ["07770", "1123", "123"])

    def test_not_transform_if_missing(self):
        spec = {"name": fields.String(default=None, transform=lambda x: str(x))}
        payload_schema = schema.generate_schema(schema.PayloadSchema, spec)()

        data = payload_schema.load({})

        self.assertEqual(data.name, None)
