# /**
#  * Copyright (c) Samsung, Inc. and its affiliates.
#  *
#  * This source code is licensed under the RESTRICTED license found in the
#  * LICENSE file in the root directory of this source tree.
#  */
from . import disco_cli_wrapper
from . import job_file_handler
from . import utils
from . import analytics


def add_job(job_name, func, args, args_types, wait=False):
    temp_dir_name =  utils.generate_temp_dir("intermediate")
    job_file_handler.create_job_temporary_files(job_name, func, args, args_types, temp_dir_name)

    output = disco_cli_wrapper.add_job_request(job_name, temp_dir_name, wait)
    if (not wait):
        ret_val = disco_cli_wrapper.add_job_parse_reply(output)
    else:
        ret_val = disco_cli_wrapper.add_wait_for_job_done_parse_reply(output)

    if ret_val:
        analytics.setup_analytics()
        analytics.track("job_register", {'id': ret_val})
    job_file_handler.remove_job_temporary_files(job_name)

    return ret_val


def start_job(job_id):
    output = disco_cli_wrapper.start_job_request(job_id)
    ret_code = disco_cli_wrapper.start_job_parse_reply(output)
    return ret_code


def wait_for_job_done(job_id):
    is_downloaded = disco_cli_wrapper.get_job_status(job_id)
    return is_downloaded


def get_results(job_name):
    return job_file_handler.get_results(job_name)
