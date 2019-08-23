"""
Job API definition
"""
import pendulum

from flask_restplus import Resource, reqparse, Namespace
from flask import current_app as app
from elasticsearch_dsl import Q

from database.queries import make_query, detailed_build_info
from models import job_model

from ..tests import AggregatedTests

ns = Namespace("job/", descriptions="Build Job")  # pylint: disable=invalid-name


@ns.route("/<path:job_name>/builds")
@ns.param("job_name", "The name of the job.")
class Job(Resource):
    """
    Defines the job resource
    """

    @ns.param("start", "RFC 3986 or ISO 8601 formatted date-time for start of time range to display over.")
    @ns.param("end", "RFC 3986 or ISO 8601 formatted date-time for end of time range to display over.")
    @ns.param("num_results", "Number of results to return (for pagination). Defaults to 25.")
    @ns.param("start_result", "First result to return (for pagination). Defaults to 0.")
    @ns.response(404, "Job not found")
    @ns.marshal_with(job_model)
    def get(self, job_name):
        """
        Retrieves a single job instance
        """
        parser = reqparse.RequestParser()
        parser.add_argument(
            "start",
            type=lambda s: pendulum.parse(s).in_timezone("UTC"),
            default=pendulum.parse("1970-01-01T00:00:00+00:00").in_timezone("UTC"),
        )
        parser.add_argument(
            "end", type=lambda s: pendulum.parse(s).in_timezone("UTC"), default=pendulum.now().in_timezone("UTC")
        )
        parser.add_argument("num_results", type=int, default=25)
        parser.add_argument("start_result", type=int, default=0)
        args = parser.parse_args()

        match_job_name = Q("term", br_job_name__raw=job_name)
        range_time = Q("range", **{"br_build_date_time": {"gte": args.start, "lt": args.end}})

        combined_filters = match_job_name & range_time

        result = make_query(
            app.config["ES_INDEX"],
            combined_filters,
            includes=detailed_build_info["includes"],
            excludes=detailed_build_info["excludes"],
            size=args.num_results,
            start=args.start_result,
        )
        if not result:
            return ns.abort(404, "Job {job} not found.".format(job=job_name))
        return {"builds": result}


@ns.route("/<path:job_name>/tests/")
@ns.param("job_name", "The name of the job.")
class JobAggregatedTests(AggregatedTests):
    """
    Collects aggregated tests from a given job
    """

    def get(self, job_name):  # pylint: disable=signature-differs
        """
        Retrieves the tests for a given job
        """
        return super().get(job_name=job_name)
