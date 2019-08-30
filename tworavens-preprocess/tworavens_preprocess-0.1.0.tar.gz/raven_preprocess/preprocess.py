"""Main module to call all sub modules"""
from os.path import abspath, dirname, join
import logging
import sys

from raven_preprocess.preprocess_runner import PreprocessRunner
from raven_preprocess.basic_utils.basic_response import (ok_resp, err_resp)
from raven_preprocess.msg_util import msg, msgt, dashes

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

CURRENT_DIR = dirname(abspath(__file__))
INPUT_DIR = join(dirname(CURRENT_DIR), 'input')
OUTPUT_DIR = join(dirname(CURRENT_DIR), 'output')


def test_run(input_file, output_filepath=None):
    """Main test run class for this module"""
    run_info = PreprocessRunner.load_from_file(input_file)

    if not run_info.success:
        msgt(run_info.err_msg)
        #print(err_resp(err_msg))
        return

    runner = run_info.result_obj

    runner.show_final_info()
    #return ok_resp(runner.get_final_json(indent=4))

    jstring = runner.get_final_json(indent=4)

    if output_filepath:
        try:
            open(output_filepath, 'w').write(jstring)
            msgt('file written: %s' % output_filepath)
        except OSError as os_err:
            msgt('Failed to write file: %s' % os_err)


def show_instructions():
    """show command line instructions"""
    info = """
--------------------------
preprocess a single file
--------------------------

# write output to screen
> python preprocess.py [input csv file]

# write output to screen and file
> python preprocess.py [input csv file] [output file name]

OR

# test input and output files
> python preprocess.py test

"""
    print(info)

if __name__ == '__main__':

    if len(sys.argv) == 2:
        if sys.argv[1] == 'test':
            input_csv = join(INPUT_DIR, 'test_file_01.csv')
            output_file = join(OUTPUT_DIR, 'test_file_01_preprocess.json')
            test_run(input_csv, output_file)
        else:
            test_run(sys.argv[1])

    elif len(sys.argv) == 3:
        test_run(sys.argv[1], sys.argv[2])
    else:
        show_instructions()
