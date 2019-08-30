"""
Collection of models for the ebr-board
"""
# pylint: disable=invalid-name
from flask_restplus import fields, Namespace

ns = Namespace("models", descriptions="Object models.")  # pylint: disable=invalid-name

tests_summary = ns.model(
    "tests_summary",
    {
        "passed_count": fields.Integer(
            attribute="br_total_passed_count", description="Total number of tests that passed in this build."
        ),
        "failed_count": fields.Integer(
            attribute="br_total_failed_count", description="Total number of tests that failed in this build."
        ),
        "skipped_count": fields.Integer(
            attribute="br_total_skipped_count", description="Total number of tests that were skipped in this build."
        ),
        "total_count": fields.Integer(attribute="br_total_count", description="Total number of tests for this build."),
    },
)

build_model = ns.model(
    "build",
    {
        "platform": fields.String(attribute="br_platform", description="Platform this build executed on."),
        "job_name": fields.String(attribute="br_job_name", description="Job this build belongs to."),
        "build_date_time": fields.DateTime(
            attribute="br_build_date_time", dt_format=u"iso8601", description="ISO 8601 formatted date-time."
        ),
        "job_url_key": fields.String(attribute="br_job_url_key", description="URL to this build in the build system"),
        "build_id_key": fields.String(attribute="br_build_id_key", description="Key for this build."),
        "status_key": fields.String(attribute="br_status_key", description="Status of the whole build."),
        "test_summary": fields.Nested(
            tests_summary,
            attribute="br_tests_object.br_summary_object",
            description="Summary of test execution for this build.",
        ),
    },
)

job_model = ns.model(
    "job", {"builds": fields.List(fields.Nested(build_model), description="List of builds associated with this job.")}
)

test_model = ns.model(
    "test",
    {
        "suite": fields.String(attribute="br_suite", description="Suite this test belongs to."),
        "test": fields.String(attribute="br_test", description="Name of the test."),
        "classname": fields.String(attribute="br_classname", description="Classname of the test."),
        "result": fields.String(atribute="br_result", description="Result (status) of the test."),
        "message": fields.String(attribute="br_message", description="Message from the test (where available)."),
        "duration": fields.Float(attribute="br_duration", description="Duration of the test (seconds)."),
        "report_set": fields.String(attribute="br_reportset", description="Report set the test belongs to."),
    },
)

tests_model = ns.model(
    "tests",
    {
        "failed_tests": fields.List(
            fields.Nested(test_model),
            attribute="br_tests_object.br_tests_failed_object",
            description="List of failed tests.",
        ),
        "passed_tests": fields.List(
            fields.Nested(test_model),
            attribute="br_tests_object.br_tests_passed_object",
            description="List of passed tests.",
        ),
        "skipped_tests": fields.List(
            fields.Nested(test_model),
            attribute="br_tests_object.br_tests_skipped_object",
            description="List of skipped tests.",
        ),
    },
)

test_agg_model = ns.model(
    "test", {"full_name": fields.String(attribute="key"), "count": fields.Integer(attribute="doc_count")}
)

tests_agg_model = ns.model("tests", {"tests": fields.List(fields.Nested(test_agg_model))})
