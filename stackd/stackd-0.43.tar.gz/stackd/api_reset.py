from .run_shell import run_shell
from .api_deploy import api_deploy

def api_reset(files_compose=[], env_vars={}, args=[]):
  run_shell(['docker-stack-rm',env_vars['STACKD_STACK_NAME'],args])
  run_shell(['docker-stack-volumes-cleanup',env_vars['STACKD_STACK_NAME']])
  api_deploy(files_compose, env_vars, args)