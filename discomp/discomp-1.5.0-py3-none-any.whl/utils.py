# /**
#  * Copyright (c) Samsung, Inc. and its affiliates.
#  *
#  * This source code is licensed under the RESTRICTED license found in the
#  * LICENSE file in the root directory of this source tree.
#  */
import os
import subprocess
import sys
import errno
import time


def get_process_args_type():
    return 'process_args_type'


def get_map_args_type():
    return 'map_args_type'


def get_starmap_args_type():
    return 'starmap_args_type'


def get_input_file_name_prefix():
    input_file_name_prefix = 'input-data'
    return input_file_name_prefix


def get_script_file_name(job_name):
    script_file_name_suffix = '-script.py'
    return job_name + script_file_name_suffix


def get_module_file_name():
    module_file_name = 'customer-module.pickle'
    return module_file_name


def get_unique_job_name(name):
    return (name + str(time.time()))


def subprocess_send_command(cmd_args, print_output=True, input=''):

    if input:
        p = subprocess.Popen(cmd_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if sys.version_info >= (3, 0):
            output = p.communicate(input.encode())[0].decode()
        else:
            output = p.communicate(input)[0]
    else:
        output = subprocess.check_output(cmd_args).decode("utf-8")

    return output


def send_command(cmd_args, print_output=True, input=''):
    output = ''
    try:
        output = subprocess_send_command(cmd_args, print_output, input)
        if print_output:
            print('%s' % output)

    except Exception as error:
        if (hasattr(error, 'errno') and error.errno == errno.ENOENT):
            print(error)
            print('Dis.co is not installed, Please install it first.')
            print('For more information, please contact us in: https://www.dis.co')
        else:
            print(error)

    return output


def generate_temp_dir(prefix="intemediate"):
    tempdir_name = "{}_{:d}".format(prefix, int(time.time()*1000))
    os.mkdir(tempdir_name)
    return tempdir_name
