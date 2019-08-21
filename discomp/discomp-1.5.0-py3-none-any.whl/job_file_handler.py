# /**
#  * Copyright (c) Samsung, Inc. and its affiliates.
#  *
#  * This source code is licensed under the RESTRICTED license found in the
#  * LICENSE file in the root directory of this source tree.
#  */
import inspect, sys
import os
import glob
import dill
from zipfile import ZipFile
from . import utils


def create_job_temporary_files(job_name, func, args, args_types, temp_dir="."):
    create_script_file(job_name, func, args_types, temp_dir)
    create_input_files(args, args_types, temp_dir)


def remove_job_temporary_files(job_name):
    remove_script_file(job_name)
    remove_input_files()


def create_script_file(job_name, func, args_types, temp_dir):
    if (func):
        script_name = temp_dir + "/" + utils.get_script_file_name(job_name)
        multiple = '' if args_types == utils.get_map_args_type() else '*'
        with open(utils.get_module_file_name(), 'wb') as f_module:
            dill.dump(inspect.getmodule(func), f_module)
        file_script = open(script_name, "w")
        script_content = '#!/usr/bin/python3.6\n' if (sys.version_info >= (3, 0)) else '#!/usr/bin/python2.7\n'
        script_content += """
import sys, dill
with open(sys.argv[1], "rb") as f_arg:
    arg = dill.load(f_arg)
with open('customer-module.pickle', 'rb') as f_module:
    module = dill.load(f_module)
"""
        script_content += 'func = getattr(module, "' + func.__name__ + '")\n'
        script_content += 'result = func(' + multiple + 'arg)'
        script_content += """
with open('run-result/result.pickle', 'wb') as f_result:
    dill.dump(result, f_result)   
"""
        file_script.write(script_content)
        file_script.close()


def create_input_files(args, args_types, temp_dir):
    if args_types == utils.get_process_args_type():
        create_input_file(args, temp_dir)
    else:
        i = -1
        for i, arg in enumerate(args):
            arg_to_dump = tuple(arg) if (args_types == utils.get_starmap_args_type()) else arg
            create_input_file(arg_to_dump, temp_dir, i)


def create_input_file(arg, temp_dir, i=0):
    input_filename = temp_dir + "/" + utils.get_input_file_name_prefix() + str(i) + '.pickle'
    with open(input_filename, 'wb') as f_arg:
        dill.dump(arg, f_arg)


def remove_script_file(job_name, temp_dir="."):
    script_name = temp_dir + "/" + utils.get_script_file_name(job_name)
    if os.path.exists(script_name):
        os.remove(script_name)

    module_file_name = temp_dir + "/" + utils.get_module_file_name()
    if os.path.exists(module_file_name):
        os.remove(module_file_name)


def remove_input_files(temp_dir="."):
    for filename in glob.glob(temp_dir + "/" + utils.get_input_file_name_prefix() + "*"):
        os.remove(filename)


def get_results(job_name):
    results = []
    job_dirs = glob.glob('*' + job_name + '*')
    if (job_dirs == []):
        return []
    [job_dir] = job_dirs
    job_results_path = job_dir + '/results'
    if os.path.exists(job_results_path):
        task_dirs = sorted(os.listdir(job_results_path))
        for task_dir in task_dirs:
            task_zip_file = os.path.join(job_results_path, task_dir)
            with ZipFile(task_zip_file, 'r') as zip:
                zip.extract('result.pickle')
                with open('result.pickle', 'rb') as f_result:
                    result = dill.load(f_result)
                    results.append(result)
        if os.path.exists('result.pickle'):
            os.remove('result.pickle')
    return results
