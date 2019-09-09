import uuid
import json
from yellow_idea_py import helper, crud, aws_s3_upload
from flask import jsonify
from datetime import datetime as dt, timedelta


def upload_to_s3(bucket_name, folder_name, _id, img_url):
    # ================================================== #
    # Upload to S3
    # ================================================== #
    file_name = str(_id) + '-' + str(uuid.uuid1())
    res_upload = aws_s3_upload.upload64(bucket_name, folder_name, file_name, img_url)
    if res_upload['status'] == 'ok':
        return res_upload['url']
    else:
        return None


def gen_file_json(key, data_list, path_file='/tmp/loyalty_1901_tesco_app_init.json'):
    data = {}
    try:
        open(path_file, 'r')
    except IOError:
        with open(path_file, 'w') as outfile:
            json.dump(data, outfile, cls=helper.MyJSONEncoder)
    # Read
    with open(path_file, 'r') as json_file:
        data = json.load(json_file)
    json_file.close()
    # Write
    data[key] = data_list
    with open(path_file, 'w') as outfile:
        json.dump(data, outfile, cls=helper.MyJSONEncoder)
    outfile.close()
    return jsonify(data=data), 200


def get_created_at():
    return (dt.today() + timedelta(hours=7)).isoformat()


def function_generate_excel(bucket_name, excel_data, file_name):
    return aws_s3_upload.upload_excel(
        json_data=excel_data,
        bucket_name=bucket_name,
        file_name=aws_s3_upload.convert_date_to_filename(get_created_at()) + " " + file_name,
        empty_col="0"
    )
