"""
Collection of functions retrieving tests aggregated independently of build and job associations.
"""
import pendulum
from flask_restplus import reqparse, Resource, Namespace
from flask import current_app as app
from elasticsearch_dsl import Q, A

from ebr_connector.schema.build_results import BuildResults

from models import tests_agg_model
from database.queries import make_query


ns = Namespace("tests/", descriptions="Test aggregations.")  # pylint: disable=invalid-name


@ns.route("/")
@ns.param("job_name", "Job to restrict search to.")
@ns.param("start", "RFC 3986 or ISO 8601 formatted date-time for start of time range to display over.")
@ns.param("end", "RFC 3986 or ISO 8601 formatted date-time for end of time range to display over.")
@ns.param("test_status", "The status of the test, currently only able to be set to failed.")
class AggregatedTests(Resource):
    """
    Defines an aggregated test resource which how many times each test has failed
    """

    @ns.marshal_with(tests_agg_model)
    def get(self, job_name=None):
        """
        Gets the AggregatedTests instance
        """
        parser = reqparse.RequestParser()
        parser.add_argument(
            "job_name", default=None, help="Input name of job to restrict search to. Leave blank for all tests."
        )
        parser.add_argument("test_status", choices=["failed"], default=None, help='Test status must be "failed"')
        parser.add_argument(
            "start",
            type=lambda s: pendulum.parse(s).in_timezone("UTC"),
            default=pendulum.parse("1970-01-01T00:00:00+00:00").in_timezone("UTC"),
        )
        parser.add_argument(
            "end", type=lambda s: pendulum.parse(s).in_timezone("UTC"), default=pendulum.now().in_timezone("UTC")
        )
        args = parser.parse_args()

        #  Use job_name if it is passed in, since this comes from api/job/<job_name>/tests/failing
        if job_name is None:
            job_name = args.get("job_name", None)

        ## Search for "failure", "FAILURE", "unstable", "UNSTABLE"
        match_status = Q("match", br_status_key=BuildResults.BuildStatus.FAILURE.name) | Q(
            "match", br_status_key=BuildResults.BuildStatus.UNSTABLE.name
        )
        range_time = Q("range", **{"br_build_date_time": {"gte": args.start, "lt": args.end}})

        # Combine them
        combined_filter = match_status & range_time

        if job_name:
            ## Search for the exact job name
            combined_filter &= Q("term", br_job_name__raw=job_name)

        # Setup aggregation
        test_agg = A("terms", field="br_tests_object.br_tests_failed_object.br_fullname.raw")

        results = make_query(app.config["ES_INDEX"], combined_filter, includes=[], excludes=[], agg=test_agg)

        return {"tests": results.__getstate__()[0]}
