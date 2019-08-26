def patch_boto3():
    from py_jaeger_tracing.global_variables import TracingEnvironment
    from py_jaeger_tracing.utils.context import tracing_context
    from botocore.client import BaseClient

    old_impl = BaseClient._make_api_call

    def fake_impl(self, operation_name, api_params):
        with tracing_context(operation_name):
            TracingEnvironment.spans[-1].log_kv({
                'event': 'boto3',
                'api_params': api_params
            })

            return old_impl(self, operation_name, api_params)

    BaseClient._make_api_call = fake_impl
