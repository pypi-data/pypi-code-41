from datetime import datetime as dt

from django.http import QueryDict
from django.test import SimpleTestCase

from dateutil.tz import tzutc

from mbq.api_tools import exceptions, fields
from mbq.api_tools.schema import ParamSchema, generate_schema


def _make_schema(spec):
    return generate_schema(ParamSchema, spec)()


class SerializeCustomQueryParamsTests(SimpleTestCase):
    def test_parse_single_query_param(self):
        data = _make_schema({"company": fields.Int(param_name="company_id")}).load(
            QueryDict("company_id=19")
        )
        self.assertEqual(data.company, 19)

    def test_parse_multiple_query_params(self):
        mock_params = QueryDict(
            "company_id=19"
            "&telephone=132-4213-123321"
            "&recurring=true"
            "&start_date=2017-02-03T22:00:00Z"
        )

        param_schema = _make_schema(
            {
                "company": fields.Int(param_name="company_id"),
                "telephone": fields.String(),
                "is_recurring": fields.Bool(param_name="recurring"),
                "start_date": fields.DateTime(),
            }
        )
        data = param_schema.load(mock_params)

        self.assertEqual(data.company, 19)
        self.assertEqual(data.telephone, "132-4213-123321")
        self.assertEqual(data.is_recurring, True)
        self.assertEqual(data.start_date, dt(2017, 2, 3, 22, tzinfo=tzutc()))

    def test_parse_query_params_with_defaults(self):
        param_schema = _make_schema(
            {
                "company_id": fields.Int(param_name="company_id", default=1),
                "is_recurring": fields.Bool(param_name="recurring", default=False),
                "start_date": fields.DateTime(
                    param_name="start_date", default=dt(1999, 8, 12, 4, tzinfo=tzutc())
                ),
            }
        )
        data = param_schema.load(QueryDict())

        self.assertEqual(data.company_id, 1)
        self.assertEqual(data.is_recurring, False)
        self.assertEqual(data.start_date, dt(1999, 8, 12, 4, tzinfo=tzutc()))

    def test_parse_query_params_required(self):
        param_schema = _make_schema({"company_id": fields.Int(param_name="company_id")})
        with self.assertRaises(exceptions.ValidationError):
            param_schema.load(QueryDict())

    def test_parse_query_params_validate(self):
        mock_params = QueryDict("price=1000")

        param_schema = _make_schema(
            {"price": fields.Int(param_name="price", validate=lambda n: n < 100)}
        )
        with self.assertRaises(exceptions.ValidationError):
            param_schema.load(mock_params)

    def test_datetime_query_param(self):
        param_schema = _make_schema({"foo": fields.DateTime()})

        # Fails if there's no timezone
        with self.assertRaises(exceptions.ValidationError):
            param_schema.load(QueryDict("foo=2017-02-03T22:00:0"))

    def test_invalid_int_query_param(self):
        param_schema = _make_schema({"foo": fields.Int()})

        with self.assertRaises(exceptions.ValidationError):
            param_schema.load(QueryDict("foo=bar"))

    def test_invalid_bool_query_param(self):
        param_schema = _make_schema({"foo": fields.Bool()})

        with self.assertRaises(exceptions.ValidationError):
            param_schema.load(QueryDict("foo=bar"))

    def test_invalid_date_query_param(self):
        param_schema = _make_schema({"foo": fields.DateTime()})

        with self.assertRaises(exceptions.ValidationError):
            param_schema.load(QueryDict("foo=bar"))


class SerializeListQueryParamTests(SimpleTestCase):
    def test_basic_input(self):
        """Basic/happy path tests."""
        mock_params = QueryDict("ids=1,2,3")

        param_schema = _make_schema({"ids": fields.Int(many=True)})
        query_params = param_schema.load(mock_params)

        self.assertEqual(query_params.ids, [1, 2, 3])

    def test_handles_different_inputs(self):
        """Make sure that we handle csv and standard list inputs."""
        mock_params = QueryDict("building_ids=one,two,three&ids=1&ids=2&ids=3")

        param_schema = _make_schema(
            {"building_ids": fields.String(many=True), "ids": fields.Int(many=True)}
        )
        query_params = param_schema.load(mock_params)

        self.assertEqual(query_params.building_ids, ["one", "two", "three"])
        self.assertEqual(query_params.ids, [1, 2, 3])

    def test_query_params_types(self):
        """Make sure it can handle any of the basic types."""
        mock_params = QueryDict(
            "ids=1&ids=42&ids=158"
            "&person_id=123&person_id=456&person_id=789"
            "&validated=false&validated=true"
            "&start_date=2017-02-03T22:00:00Z&start_date=1987-11-24T23:50:00Z"
        )

        param_schema = _make_schema(
            {
                "company_ids": fields.Int(many=True, param_name="ids"),
                "person_ids": fields.String(many=True, param_name="person_id"),
                "is_validated": fields.Bool(many=True, param_name="validated"),
                "start_dates": fields.DateTime(many=True, param_name="start_date"),
            }
        )
        query_params = param_schema.load(mock_params)

        def assert_type(value_type, values):
            return all(type(value) == value_type for value in values)

        self.assertEqual(query_params.company_ids, [1, 42, 158])
        self.assertEqual(query_params.person_ids, ["123", "456", "789"])
        self.assertEqual(query_params.is_validated, [False, True])
        self.assertEqual(
            query_params.start_dates,
            [
                dt(2017, 2, 3, 22, tzinfo=tzutc()),
                dt(1987, 11, 24, 23, 50, tzinfo=tzutc()),
            ],
        )

        assert_type(int, query_params.company_ids)
        assert_type(str, query_params.person_ids)
        assert_type(bool, query_params.is_validated)
        assert_type(dt, query_params.start_dates)

    def test_handles_default_values(self):
        param_schema = _make_schema(
            {"ids": fields.Int(many=True, param_name="buildings", default=[1, 2])}
        )
        query_params = param_schema.load(QueryDict())

        self.assertEqual(query_params.ids, [1, 2])

    def test_required_raises(self):
        """Handles that marking as required will correctly raise."""

        param_schema = _make_schema({"ids": fields.Int(many=True)})

        with self.assertRaises(exceptions.ValidationError):
            param_schema.load(QueryDict())

    def test_validation_raises(self):
        """Make sure the correct exception raises if validation fails."""
        VALID_STATUSES = ["active", "approved"]

        def validate_status(statuses):
            if not all(status in VALID_STATUSES for status in statuses):
                raise exceptions.ValidationError("Invalid status!")

        param_schema = _make_schema(
            {"partner_status": fields.String(many=True, validate=validate_status)}
        )

        with self.assertRaises(exceptions.ValidationError):
            param_schema.load(QueryDict("partner_status=registered"))

    def test_unserializable_value_raises(self):
        """Unserializable inputs should always raise"""
        param_schema = _make_schema({"ids": fields.Int(many=True)})

        with self.assertRaises(exceptions.ValidationError):
            param_schema.load(QueryDict("ids=one,two,three"))


class SerializePaginatedQueryParamsTests(SimpleTestCase):
    def test_simple_pagination(self):
        param_schema = _make_schema({"page": fields.Int(), "page_size": fields.Int()})
        pagination = param_schema.load(QueryDict("page=1&page_size=10")).pagination

        self.assertEqual(pagination.page, 1)
        self.assertEqual(pagination.page_size, 10)

    def test_default_pagination(self):
        param_schema = _make_schema(
            {"page": fields.Int(default=2), "page_size": fields.Int(default=25)}
        )
        pagination = param_schema.load(QueryDict()).pagination

        self.assertEqual(pagination.page, 2)
        self.assertEqual(pagination.page_size, 25)
