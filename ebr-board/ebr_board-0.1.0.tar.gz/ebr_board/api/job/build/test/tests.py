"""
Tests API definition
"""
from flask_restplus import reqparse, Resource, Namespace
from flask import current_app as app
from elasticsearch_dsl import Q

from models import tests_model
from database.queries import make_query


ns = Namespace(  # pylint: disable=invalid-name
    "job/<path:job_name>/buildid/<build_id>/tests/", descriptions="Test results"
)


@ns.route("/")
@ns.param("job_name", "The name of the job this build belongs to.")
@ns.param("build_id", "The id of the specific build being retrieved.")
@ns.param("test_status", "The status of the test, passed, failed or skipped. Leave blank for all.")
class Tests(Resource):
    """
    Operations for Test objects
    """

    @ns.response(404, "Test not found")
    @ns.response(400, "Invalid path")
    @ns.marshal_with(tests_model)
    def get(self, job_name, build_id):
        """
        Retrieves a collection of tests.
        """
        parser = reqparse.RequestParser()
        parser.add_argument(
            "test_status",
            choices=["passed", "failed", "skipped"],
            default=None,
            help='Test status must be "passed", "failed", or "skipped". Leave blank for all tests.',
        )
        args = parser.parse_args()

        include_tests = []
        if args.test_status == "failed" or args.test_status is None:
            include_tests.append("br_tests_object.br_tests_failed_object.*")
        if args.test_status == "passed" or args.test_status is None:
            include_tests.append("br_tests_object.br_tests_passed_object.*")
        if args.test_status == "skipped" or args.test_status is None:
            include_tests.append("br_tests_object.br_tests_skipped_object.*")

        build_details = {"includes": include_tests, "excludes": []}

        match_job_name = Q("term", br_job_name__raw=job_name)
        match_build_id = Q("term", br_build_id_key=build_id)
        combined_filter = match_job_name + match_build_id
        result = make_query(
            app.config["ES_INDEX"],
            combined_filter,
            includes=build_details["includes"],
            excludes=build_details["excludes"],
        )
        if not result:
            return ns.abort(
                404, "Tests for Build #{build} for job {job} not found.".format(build=build_id, job=job_name)
            )

        return result[0]
