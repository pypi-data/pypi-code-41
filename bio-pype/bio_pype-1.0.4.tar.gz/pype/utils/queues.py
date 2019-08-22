import os
import sys
import yaml
from pype.misc import generate_uid
from time import sleep
from distutils.spawn import find_executable


def yaml_dump(command, requirements, dependencies, log, profile):
    pype_exec = find_executable('pype')
    if pype_exec is None:
        pype_exec = '%s -m pype.commands' % sys.executable
    command = '%s --profile %s snippets --log %s %s' % (
        pype_exec, profile, log.__path__, command)
    run_id = generate_uid(10)[-10:]
    log.log.info('Queue yaml_dump, command: %s' % command)
    log.log.info('Queue yaml_dump, requirements: %s' % requirements)
    log.log.info('Queue yaml_dump, dependencies: %s' % dependencies)
    log.log.info('Queue yaml_dump, run ID: %s' % run_id)
    root_dir, base_name = os.path.split(log.__path__)
    yaml_file = os.path.join(root_dir, 'pipeline_runtime.yaml')
    if os.path.isfile(yaml_file):
        with open(yaml_file, 'rt') as pipeline_runtime:
            runtime = yaml.safe_load(pipeline_runtime)
    else:
        runtime = dict()
    runtime[run_id] = dict()
    runtime[run_id]['command'] = command
    runtime[run_id]['requirements'] = requirements
    runtime[run_id]['dependencies'] = dependencies
    with open(yaml_file, 'wt') as pipeline_runtime:
        yaml.dump(runtime, pipeline_runtime, default_flow_style=False)
    sleep(1)
    return(run_id)
