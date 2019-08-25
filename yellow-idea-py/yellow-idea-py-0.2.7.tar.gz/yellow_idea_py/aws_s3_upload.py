import base64
import logging
import os
import uuid

import boto3
from botocore.exceptions import ClientError
from yellow_idea_py.helper import is_local
import xlsxwriter

if is_local:
    s3_client = boto3.client('s3',
                             aws_access_key_id=os.environ['ACCESS_KEY_ID'],
                             aws_secret_access_key=os.environ['SECRET_ACCESS_KEY'])
else:
    s3_client = boto3.client('s3')


def upload_file(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = file_name
    try:
        s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def get_file_type(data):
    a = data.split(';base64,')
    if a[0] == 'data:image/png':
        return ['png', a[1]]
    elif a[0] == 'data:image/svg+xml':
        return ['png', a[1]]
    elif a[0] == 'data:image/jpeg':
        return ['jpg', a[1]]
    else:
        return ['', a[1]]


def upload_normal(bucket_name, region, folder_name, file_name):
    tmp_filename = '/tmp/' + file_name
    real_filename = folder_name + file_name
    if upload_file(tmp_filename, bucket_name, real_filename):
        os.remove(tmp_filename)
        return {
            'status': 'ok',
            'url': "https://s3-%s.amazonaws.com/%s/%s" % (region, bucket_name, real_filename)
        }
    else:
        return {
            'status': 'fail',
            'message': 'upload fail'
        }


def upload64(bucket_name, folder_name, file_name, data):
    file = get_file_type(data)
    tmp_filename = '/tmp/' + file_name + '.' + file[0]
    real_filename = folder_name + file_name + '.' + file[0]
    with open(tmp_filename, 'wb+') as f:
        f.write(base64.b64decode(file[1]))
        f.close()
    if upload_file(tmp_filename, bucket_name, real_filename):
        location = s3_client.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
        os.remove(tmp_filename)
        return {
            'status': 'ok',
            'url': "https://s3-%s.amazonaws.com/%s/%s" % (location, bucket_name, real_filename)
        }
    else:
        return {
            'status': 'fail',
            'message': 'upload fail'
        }


def convert_date_to_filename(d):
    a = str(d).split('T')
    _date = a[0].split('-')
    _t = a[1].split(':')
    _time = _t[0] + _t[1]
    s = ""
    result = s.join(_date)
    return result + _time


def upload_excel(json_data, bucket_name, file_name):
    if len(json_data) > 0:
        file_name = file_name + ".xlsx"
        tmp_filename = '/tmp/' + file_name
        real_filename = 'excel/' + str(uuid.uuid1()) + '/' + file_name
        workbook = xlsxwriter.Workbook(tmp_filename)
        worksheet = workbook.add_worksheet()
        header_title = []
        col_head = 0
        # Create Header
        for (i, v) in enumerate(json_data[0]):
            header_title.append(v)
            worksheet.write(0, col_head, str(v))
            col_head = col_head + 1
        # Create Rows
        row = 1
        for item in json_data:
            col = 0
            for head in header_title:
                worksheet.write(row, col, str(item[head]))
                col = col + 1
            row = row + 1
        workbook.close()
        if upload_file(tmp_filename, bucket_name, real_filename):
            location = s3_client.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
            os.remove(tmp_filename)
            return {
                'status': 'ok',
                'url': "https://s3-%s.amazonaws.com/%s/%s" % (location, bucket_name, real_filename)
            }
        else:
            return {
                'status': 'fail',
                'message': 'upload fail'
            }
    else:
        return {
            'status': 'fail',
            'message': 'no data'
        }
