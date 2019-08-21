# /**
#  * Copyright (c) Samsung, Inc. and its affiliates.
#  *
#  * This source code is licensed under the RESTRICTED license found in the
#  * LICENSE file in the root directory of this source tree.
#  */
import os
from . import utils


def disco_login():
    user = os.environ.get('DISCO_LOGIN_USER')
    password = os.environ.get('DISCO_LOGIN_PASSWORD')
    if (user is None or password is None):
        print('Please use your credentials to login to dis.co')
        return False

    login_success_output = 'Logged in as'
    # 'Login' to cli 
    output = utils.send_command(['disco', 'login', '-u', user, '-p', password], False)
    if login_success_output in output:
        return True
    else:
        print('%s' % output)
        return False


def disco_cli(cmd_args, print_output=True, input=''):
    if disco_login():
        output = utils.send_command(cmd_args, print_output, input)
        return output


def add_job_request(job_name, temp_dir=".", wait=False):
    machine_size = os.environ.get('DISCO_MACHINE_SIZE')
    script_name = temp_dir + "/" + utils.get_script_file_name(job_name)
    input_files = temp_dir + "/" + utils.get_input_file_name_prefix() + "*"  # "input-data*"
    cmd = ['disco', 'add', '-n', job_name, '-s', script_name, '-i', input_files, '-t', utils.get_module_file_name(),
           '-t', 'requirements.txt']
    cmd += ['--clusterInstanceType', str(machine_size)] if machine_size else []
    cmd += ['-w', '-d'] if wait else []
    input = 'Yes' if wait else ''
    output = disco_cli(cmd, True, input)
    return output


def add_job_parse_reply(output):
    job_id = ''
    if output and 'successfully' in output:
        # Parse the added job id from the response (in the 3rd line) 
        lines = output.splitlines()
        if len(lines) > 2 and ('jobId' in lines[2]):
            a, b = lines[2].split('[')
            job_id = b.replace(']', '')
    return job_id


def add_wait_for_job_done_parse_reply(output):
    lines = list(filter(lambda line: 'jobId' in line, output.splitlines()))
    if len(lines) == 0:
        return False
    job_id = lines[0]
    for el in ['jobId', '\'', '[', ']', ' ', ':']:
        job_id = job_id.replace(el, '')
    if 'Failed' in output:
        return False
    return job_id


def start_job_request(job_id):
    output = disco_cli(['disco', 'start', '-j', job_id])
    return output


def start_job_parse_reply(output):
    return output and 'started successfully' in output


def get_job_status(job_id):
    is_downloaded = False
    cmd = ['disco', 'view', '-j', job_id, '-w']
    output = disco_cli(cmd, False)

    # Job is done
    if output and 'Done' in output:
        if 'Success' in output:  # At least one of the tasks has succeeded
            # Download the results
            cmd = ['disco', 'view', '-j', job_id, '-d']
            disco_cli(cmd, True, 'Yes')  # 'Yes' will overwrite existing directory result (with the same job name)
            is_downloaded = True
        else:  # All tasks failed
            cmd = ['disco', 'view', '-j', job_id]
            disco_cli(cmd)
            is_downloaded = False

    return is_downloaded
