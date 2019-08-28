import sys
import subprocess

from .run_shell import run_shell

def api_vc(env_vars={}):

  process = run_shell([
    'docker-stack-volumes-cleanup',
    env_vars['STACKD_STACK_NAME'],
  ])
  if(process.returncode != 0):
      sys.exit(process.returncode)