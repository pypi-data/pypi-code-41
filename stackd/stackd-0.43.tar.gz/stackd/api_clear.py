from .run_shell import run_shell

def api_clear(env_vars={}):
  run_shell(['docker-stack-rm',env_vars['STACKD_STACK_NAME']])
  run_shell(['docker-stack-volumes-cleanup',env_vars['STACKD_STACK_NAME']])