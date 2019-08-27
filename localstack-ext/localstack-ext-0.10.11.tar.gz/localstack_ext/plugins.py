import os
bNiOk=Exception
bNiOa=any
bNiOM=True
from localstack.utils import bootstrap
from localstack_ext import config as config_ext
from localstack_ext.bootstrap import licensing,cli
def register_localstack_plugins():
 with licensing.prepare_environment():
  try:
   from localstack_ext.services import dns_server
   dns_server.setup_network_configuration()
  except bNiOk as e:
   print(e)
   return
  try:
   from localstack.services.infra import register_plugin,Plugin
   from localstack.services.apigateway import apigateway_listener
   from localstack_ext.services.cognito import cognito_starter,cognito_idp_api,cognito_listener
   from localstack_ext.services.iam import iam_starter
   from localstack_ext.services.sts import sts_starter
   from localstack_ext.services.elasticache import elasticache_starter
   from localstack_ext.services.rds import rds_starter,rds_listener
   from localstack_ext.services.awslambda import lambda_extended
   from localstack_ext.services.sqs import sqs_extended
   from localstack_ext.services.apigateway import apigateway_extended
   from localstack_ext.services.cloudformation import cloudformation_extended
   from localstack_ext.services import edge
   apigateway_listener.UPDATE_APIGATEWAY.forward_request=cognito_idp_api.wrap_api_method('apigateway',apigateway_listener.UPDATE_APIGATEWAY.forward_request)
   register_plugin(Plugin('rds',start=rds_starter.start_rds,listener=rds_listener.UPDATE_RDS))
   register_plugin(Plugin('sts',start=sts_starter.start_sts))
   register_plugin(Plugin('iam',start=iam_starter.start_iam))
   register_plugin(Plugin('cognito-idp',start=cognito_starter.start_cognito_idp,listener=cognito_listener.UPDATE_COGNITO))
   register_plugin(Plugin('cognito-identity',start=cognito_starter.start_cognito_identity,listener=cognito_listener.UPDATE_COGNITO_IDENTITY))
   register_plugin(Plugin('elasticache',start=elasticache_starter.start_elasticache))
   register_plugin(Plugin('edge',start=edge.start_edge))
   lambda_extended.patch_lambda()
   sqs_extended.patch_sqs()
   apigateway_extended.patch_apigateway()
   cloudformation_extended.patch_cloudformation()
  except bNiOk as e:
   print(e)
   return
 docker_flags=('-p {dns_addr}:{dns_port}:{dns_port} -p {dns_addr}:{dns_port}:{dns_port}/udp').format(dns_addr=config_ext.DNS_ADDRESS,dns_port=dns_server.DNS_PORT)
 if bNiOa([is_api_enabled(api)for api in('rds','elasticache')]):
  docker_flags+=' -p {start}-{end}:{start}-{end}'.format(start=config_ext.SERVICE_INSTANCES_PORTS_START,end=config_ext.SERVICE_INSTANCES_PORTS_END)
 result={'docker':{'run_flags':docker_flags}}
 return result
def is_api_enabled(api):
 apis=bootstrap.canonicalize_api_names()
 for a in apis:
  if a==api or a.startswith('%s:'%api):
   return bNiOM
def register_localstack_commands():
 if os.environ.get('LOCALSTACK_API_KEY'):
  cli.register_commands()
 return bNiOM
# Created by pyminifier (https://github.com/liftoff/pyminifier)
