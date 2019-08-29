import argparse
import csv
import fnmatch
import logging
import os
import tarfile

from configobj import ConfigObj, ConfigObjError


__version__ = '1.0.1'


STUDENT_INFO_FILENAME = 'student-info.ini'
STUDENT_INFO_KEYS = ['tar_name', 'student_id', 'first_name', 'last_name', 'email']


def find_filenames(path, filename_pattern):
    file_list = os.listdir(path)
    for name in fnmatch.filter(file_list, filename_pattern):
        yield os.path.join(path, name)

def open_tar_archives(filenames):
    for name in filenames:
        yield tarfile.open(name, errorlevel=1)

def open_inner_tar_archives(tar_archives, filename_pattern):
    for tar in tar_archives:
        for name in fnmatch.filter(tar.getnames(), filename_pattern):
            inner_tar_fileobj = tar.extractfile(name)
            yield name, tarfile.open(fileobj=inner_tar_fileobj, errorlevel=1)

def open_student_info_files(inner_tar_archives, student_info_filename=STUDENT_INFO_FILENAME):
    for tar_name, tar in inner_tar_archives:
        names = fnmatch.filter(tar.getnames(), '*/' + student_info_filename)

        num_names = len(names)
        if num_names == 0:
            logging.warn("No student found in '%s', or s/he has not saved any '%s' files", tar_name, student_info_filename)
        elif num_names > 1:
            logging.error("Student in '%s' has saved %d '%s' files", tar_name, num_names, student_info_filename)
        else:
            yield tar_name, tar.extractfile(names[0])

def parse_student_info_files(student_info_files):
    for tar_name, fileobj in student_info_files:
        try:
            student_info = ConfigObj(
                fileobj,
                list_values=False,
                interpolation=False,
                raise_errors=True
            ).dict()
            student_info.update(tar_name=tar_name)
            yield student_info
        except ConfigObjError, e:
            logging.error("Student in '%s' has saved an invalid file: %s", tar_name, e)

def validate_student_info(student_info):
    for student in student_info:
        missing_keys = [k for k in STUDENT_INFO_KEYS if not student.get(k)]
        if missing_keys:
            logging.error("Student in '%s' has not provided the following data: %s", student['tar_name'], ', '.join(missing_keys))
        else:
            yield student

def normalize_student_id(s):
    # Remove spaces
    s = s.replace(' ', '')

    # Normalize the year separator to our labs internal format (i.e. 'ra98/2015' to 'ra98-2015')
    s = s.replace('/', '-')

    # We prefer lowecase ids
    s = s.lower()

    return s

def normalize_student_ids(student_info):
    for student in student_info:
        student['student_id'] = normalize_student_id(student['student_id'])
        yield student

def get_student_info(tar_path):
    tar_filenames = find_filenames(tar_path, '*.tar')
    tar_archives = open_tar_archives(tar_filenames)
    inner_tar_archives = open_inner_tar_archives(tar_archives, '*.tgz')
    student_info_files = open_student_info_files(inner_tar_archives)
    student_info = parse_student_info_files(student_info_files)
    student_info = validate_student_info(student_info)
    student_info = normalize_student_ids(student_info)

    return student_info

def store_results_to(results_filename, student_info):
    with open(results_filename, 'w') as out:
        writer = csv.DictWriter(out, fieldnames=STUDENT_INFO_KEYS)

        writer.writeheader()
        writer.writerows(student_info)

def main():
    # Setup command line option parser
    parser = argparse.ArgumentParser(
        description='Harvests email addresses of our ACS students, from within the lab.'
    )
    parser.add_argument(
        'results_filename',
        help="Store results in the selected filename, in CSV format"
    )
    parser.add_argument(
        '-t',
        '--tar-path',
        metavar='<directory>',
        default='.',
        help='Search the selected <directory> for TAR exam archives, current working directory by default'
    )
    parser.add_argument(
        '-q',
        '--quiet',
        action='store_const',
        const=logging.WARN,
        dest='verbosity',
        help='Be quiet, show only warnings and errors'
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_const',
        const=logging.DEBUG,
        dest='verbosity',
        help='Be very verbose, show debug information'
    )
    parser.add_argument(
        '--version',
        action='version',
        version="%(prog)s " + __version__
    )
    args = parser.parse_args()

    # Configure logging
    log_level = args.verbosity or logging.INFO
    logging.basicConfig(level=log_level, format="[%(levelname)s] %(message)s")

    student_info = get_student_info(args.tar_path)
    store_results_to(args.results_filename, student_info)

if __name__ == '__main__':
    main()
