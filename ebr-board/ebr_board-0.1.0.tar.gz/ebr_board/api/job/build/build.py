"""
Build API definitions
"""
from flask_restplus import Resource, Namespace
from flask import current_app as app
from elasticsearch_dsl import Q

from models import build_model
from database.queries import make_query, detailed_build_info

ns = Namespace(  # pylint: disable=invalid-name
    "job/<path:job_name>/build", descriptions="Build results"
)


@ns.route("/<build_id>/")
@ns.param("job_name", "The name of the job this build belongs to.")
@ns.param("build_id", "The id of the specific build being retrieved.")
class Build(Resource):
    """
    Build objects definition
    """

    @ns.response(404, "Build not found")
    @ns.marshal_with(build_model)
    def get(self, job_name, build_id):
        """
        Retrieves a single Build object
        """
        match_job_name = Q("term", br_job_name__raw=job_name)
        match_build_id = Q("term", br_build_id_key=build_id)
        combined_filter = match_job_name + match_build_id
        result = make_query(
            app.config["ES_INDEX"],
            combined_filter,
            includes=detailed_build_info["includes"],
            excludes=detailed_build_info["excludes"],
        )
        if not result:
            return ns.abort(
                404,
                "Build #{build} for job {job} not found.".format(
                    build=build_id, job=job_name
                ),
            )
        return result[0].__getstate__()[0]
