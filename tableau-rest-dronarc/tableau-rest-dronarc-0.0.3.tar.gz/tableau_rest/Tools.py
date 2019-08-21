import xml.etree.ElementTree as ET  # Contains methods used to build and parse XML
import requests  # Contains methods used to make HTTP requests

import sys
import os
import math
import logging
#import psycopg2
import re
from reference import version
from pythonjsonlogger import jsonlogger

#from google.cloud import storage
#from google.cloud import bigquery

# The following packages are used to build a multi-part/mixed request.
# They are contained in the 'requests' library
from requests.packages.urllib3.fields import RequestField
from requests.packages.urllib3.filepost import encode_multipart_formdata

"""
Class/container for all generic functions. Basically holds anything expected to be used multiple times across 
tableau_rest/scripts. 
"""
XMLNS = {'t': 'http://tableau.com/api'}
VERSION = version.VERSION


def encode_for_display(text):
    """
    Encodes strings so they can display as ASCII in a Windows terminal window.
    This function also encodes strings for processing by xml.etree.ElementTree functions.

    Returns an ASCII-encoded version of the text.
    Unicode characters are converted to ASCII placeholders (for example, "?").
    """
    return text.encode('ascii', errors="backslashreplace").decode('utf-8')


def check_status(server_response, success_code):
    """
    Checks the server response for possible errors.

    'server_response'       the response received from the server
    'success_code'          the expected success code for the response
    Throws an ApiCallError exception if the API call fails.
    """
    if server_response.status_code != success_code:
        parsed_response = ET.fromstring(server_response.text)

        # Obtain the 3 xml tags from the response: error, summary, and detail tags
        error_element = parsed_response.find('t:error', namespaces=XMLNS)
        summary_element = parsed_response.find('.//t:summary', namespaces=XMLNS)
        detail_element = parsed_response.find('.//t:detail', namespaces=XMLNS)

        # Retrieve the error code, summary, and detail if the response contains them
        code = error_element.get('code', 'unknown') if error_element is not None else 'unknown code'
        summary = summary_element.text if summary_element is not None else 'unknown summary'
        detail = detail_element.text if detail_element is not None else 'unknown detail'
        error_message = '{0}: {1} - {2}'.format(code, summary, detail)
        raise ApiCallError(error_message)
    return


def make_multipart(parts):
    """
    Creates one "chunk" for a multi-part upload

    'parts' is a dictionary that provides key-value pairs of the format name: (filename, body, content_type).

    Returns the post body and the content type string.

    For more information, see this post:
        http://stackoverflow.com/questions/26299889/how-to-post-multipart-list-of-json-xml-files-using-python-requests
    """
    mime_multipart_parts = []
    for name, (filename, blob, content_type) in parts.items():
        multipart_part = RequestField(name=name, data=blob, filename=filename)
        multipart_part.make_multipart(content_type=content_type)
        mime_multipart_parts.append(multipart_part)

    post_body, content_type = encode_multipart_formdata(mime_multipart_parts)
    content_type = ''.join(('multipart/mixed',) + content_type.partition(';')[1:])
    return post_body, content_type


def switch(argument):
    switcher = {
        'twbx': "workbooks",
        'tde': "datasources",
    }
    return switcher.get(argument, "")


class ApiCallError(Exception):
    """ ApiCallError """
    pass


class UserDefinedFieldError(Exception):
    """ UserDefinedFieldError """
    pass


def setup_log(output_log_file, output_log_verb_file):
    """
    Structures two log files, a verbose (debug level) log and default log (info).
    :param output_log_file:
    :param output_log_verb_file:
    :return:
    """
    # set up log
    logging.basicConfig(filename=output_log_verb_file, level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y/%m/%d %H:%M:%S')
    console_out = logging.StreamHandler(sys.stdout)
    info = logging.FileHandler(output_log_file)
    info.setLevel(logging.INFO)
    # verbose = logging.FileHandler(output_log_verb_file)
    # verbose.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
    log = logging.getLogger()
    console_out.setFormatter(StackdriverJsonFormatter())
    info.setFormatter(formatter)
    # verbose.setFormatter(formatter)
    log.addHandler(console_out)
    log.addHandler(info)
    # log.addHandler(verbose)
    return log


# def query_postgres(serverFile, queryFile, user ='', ip='', port=8060, password='',database=''):
#     """
#     Basic query function, given a postgres connection and query return the results.
#     :param serverFile:
#     :param queryFile:
#     :return:
#     """
#
#     if ip == '':
#         with open(serverFile) as f:
#             host, port, password = f.read().split('\n')
#
#     with open(queryFile) as f:
#         query = f.read()
#
#     output = []
#
#     try:
#         connection = psycopg2.connect(user=user,
#                                       password=password,
#                                       host=ip,
#                                       port=port,
#                                       database=database)
#         cursor = connection.cursor()
#
#         # Print PostgreSQL version
#         cursor.execute(query)
#         records = cursor.fetchall()
#         logging.debug("Results - {}".format(records, "\n"))
#         for r in records:
#             # output.append(r[0]) # IF ONLY RETURNING 1 FIELD
#             output.append(r)  # returns list<tuples>
#
#     except (Exception, psycopg2.Error) as error:
#         logging.error("Error while connecting to PostgreSQL: {}".format(error), exc_info=True)
#     finally:
#         # closing database connection.
#         if (connection):
#             cursor.close()
#             connection.close()
#             logging.info("PostgreSQL connection is closed")
#         return output


def clean_filename(filename):
    filename = re.sub(r'[\\/\:*"<>\|\.%\$\^&£]', '', filename)
    return filename


# def upload_to_gcs(file, bucket_name, log, service_account=""):
#     if not service_account == "":
#         storage_client = storage.Client.from_service_account_json('reference/service_account.json')
#     else:
#         storage_client = storage.Client.from_service_account_json((service_account))
#     storage_client = storage.Client()
#     bucket = storage_client.get_bucket(bucket_name)
#     blob = bucket.blob(file)
#     try:
#         blob.upload_from_filename(file)
#     except Exception as e:
#         log.error('Unable to upload {} to {}'.format(file, bucket_name))
#
#     log.info('File {} uploaded to {}.'.format(file, bucket_name))


# def upload_to_bq(filename, dataset_id, table_id):
#
#     client = bigquery.Client()
#     dataset_ref = client.dataset(dataset_id)
#     table_ref = dataset_ref.table(table_id)
#     job_config = bigquery.LoadJobConfig()
#     job_config.source_format = bigquery.SourceFormat.CSV
#     job_config.skip_leading_rows = 1
#     job_config.autodetect = True
#
#     with open(filename, 'rb') as source_file:
#         job = client.load_table_from_file(
#             source_file,
#             table_ref,
#             location='EU',  # Must match the destination dataset location.
#             job_config=job_config)  # API request
#
#     job.result()  # Waits for table load to complete.
#
#     print('Loaded {} rows into {}:{}.'.format(
#         job.output_rows, dataset_id, table_id))


class StackdriverJsonFormatter(jsonlogger.JsonFormatter, object):

    def __init__(self, fmt="%(levelname) %(message)", style='%', *args, **kwargs):
        jsonlogger.JsonFormatter.__init__(self, fmt=fmt, *args, **kwargs)

    def process_log_record(self, log_record):
        log_record['severity'] = log_record['levelname']
        # del log_record['levelname']
        return super(StackdriverJsonFormatter, self).process_log_record(log_record)
