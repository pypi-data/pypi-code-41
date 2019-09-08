import logging

from flask import request
from flask_restplus import Api, Resource, reqparse, fields
from hawking.frontend.engine.default import engine as default_engine
from hawking.frontend.engine.online import engine as online_engine
from hawking.frontend.store.default import store

log = logging.getLogger(__name__)

api = Api(version='1.0', title='Hawking API', description='Hawking powered search engine')
ns = api.namespace('hawking', description='Search engine operation')

search_arguments = reqparse.RequestParser()
search_arguments.add_argument('namespace', type=str, required=True, default=0, help='Namespace/scope')
search_arguments.add_argument('query', type=str, required=True, default=0, help='Query string')
search_arguments.add_argument('offset', type=int, required=False, default=0, help='Page offset')
search_arguments.add_argument('count', type=int, required=False, choices=[3, 10, 15, 20],
                                default=10, help='Results per page {error_msg}')

result = api.model('Result', {
    'uuid': fields.String(required=True, description='Result unique reference'),
    'score': fields.Float(required=True, description='Result score'),
})

page_of_results = api.model('Page of results', {
    'results': fields.List(fields.Nested(result)),
})

def search_records(request, engine):
    """
    Search.
    """
    args = search_arguments.parse_args(request)

    namespace = args.get('namespace')
    query = args.get('query')
    result_offset = args.get('offset', 0)
    result_count = args.get('count', 10)

    log.info('%s: search within "%s" namespace for "%s", look for %d results starting with %d offset',
                type(engine), namespace, query, result_count, result_offset)

    results = engine.search(namespace, result_offset + result_count, query)
    log.info('pre %s', results)

    results = results[result_offset:]
    log.info('post %s', results)

    responses = []
    for result in results:
        responses.append({"uuid": result[0], "score": result[1]})

    log.info('resp %s', responses)
    return {"results": responses}


@ns.route('/search')
class DefaultSearchApi(Resource):
    @api.expect(search_arguments)
    @api.marshal_with(page_of_results)
    def get(self):
        return search_records(request, default_engine)
        

@ns.route('/search/online')
class OnlineSearchApi(Resource):
    @api.expect(search_arguments)
    @api.marshal_with(page_of_results)
    def get(self):
        return search_records(request, online_engine)


record = api.model('Record', {
    'uuid': fields.String(required=True, description='Record unique reference'),
    'namespace': fields.String(required=True, description='Record namespace'),
    'content': fields.String(required=True, description='Record content'),
})

def index_record(request, engine):
    """
    Index record.
    """
    args = request.json
    namespace = args.get('namespace')
    uuid = args.get('uuid')
    content = args.get('content')

    if engine.index(namespace, uuid, content):
        log.info("%s/%s/%s: %s inserted", type(engine), namespace, uuid, content)
    else:
        log.info("%s/%s/%s: %s updated", type(engine), namespace, uuid, content)

    return None, 201

@ns.route('/index')
class IndexApi(Resource):
    @api.expect(record)
    def put(self):
        return index_record(request, default_engine)
        

@ns.route('/index/online')
class OnlineIndexApi(Resource):
    @api.expect(record)
    def put(self):
        return index_record(request, online_engine)



store_put_result = api.model('UUID of stored documents', {
    'uuid': fields.String(),
})


store_get = reqparse.RequestParser()
store_get.add_argument('namespace', type=str, required=True, default=0, help='Namespace/scope')
store_get.add_argument('uuid', type=str, required=True, default=0, help='Document unique reference')


store_get_result = api.model('Document', {
    'uuid': fields.String(),
    'content': fields.String(),
})

@ns.route('/store')
class OnlineStoreApi(Resource):
    @api.expect(record)
    @api.marshal_with(store_put_result)
    def put(self):
        """
        Store object.
        """
        args = request.json
        namespace = args.get('namespace')
        uuid = args.get('uuid')
        content = args.get('content')

        uuid = store.put(namespace, uuid, content)
        log.info("Store %s/%s: %s", namespace, uuid, content)

        return {"uuid": uuid}, 201

    @api.expect(store_get)
    @api.marshal_with(store_get_result)
    def get(self):
        """
        Search.
        """
        args = store_get.parse_args(request)

        namespace = args.get('namespace')
        uuid = args.get('uuid')

        log.info("Retrieve %s/%s", namespace, uuid)

        content = store.get(namespace, uuid)
        return {"uuid": uuid, "content": content}


@api.errorhandler(ValueError)
def value_error_handler(e):
    message = str(e)
    log.exception(message)

    return {'message': message}, 401


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(message)

    return {'message': message}, 500

