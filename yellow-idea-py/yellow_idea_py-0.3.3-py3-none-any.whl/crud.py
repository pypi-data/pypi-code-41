import uuid
from datetime import datetime, timedelta


def get_created_at():
    # return (datetime.today() + timedelta(hours=7)).isoformat()
    return (datetime.today() + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")


def convert_to_new_data(data):
    # check new data or not
    if 'id' not in data or data['id'] == '0' or data['id'] == 0:
        data['id'] = str(uuid.uuid1())
    d = get_created_at()
    if 'created_at' not in data:
        data['created_at'] = d
    data['updated_at'] = d
    return data
