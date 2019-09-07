import os
import fnmatch
import decimal
import datetime
import flask.json
from flask import session, url_for, request, get_flashed_messages, json as flask_json
from werkzeug.utils import secure_filename

assets_bucket = f"https://s3-{os.environ['SERVICE_REGION']}.amazonaws.com/{os.environ['ASSETS_BUCKET']}"


def get_session_value(a, b):
    if b in a:
        return a[b]
    else:
        return None


def get_real_js_name(path, target):
    file_name = ""
    for file in os.listdir(path):
        if fnmatch.fnmatch(file, '*.js'):
            if target in file:
                file_name = file
                break
    return file_name


def get_js_path(folder, filename):
    if 'http://localhost' in request.host_url:
        return url_for(folder, filename=filename)
    else:
        return f"{assets_bucket}/{filename}"


def get_filename_last_update(file_name):
    return '?u=' + str(os.path.getmtime(file_name))


def clear_and_get_flash_message():
    success_message = get_flashed_messages(category_filter=["success"])
    error_message = get_flashed_messages(category_filter=["error"])
    warning_message = get_flashed_messages(category_filter=["warning"])
    if '_flashes' in session:
        session.pop('_flashes', None)
    return {
        'success': success_message,
        'error': error_message,
        'warning': warning_message
    }


def route_convert(t, r):
    if t == 1:
        return f"/{r}"
    elif t == 2:
        return f"{r.replace('/', '.')}"


def uploader(p, f):
    filename = secure_filename(f.filename)
    # f.save(os.path.join(p, filename))
    f.save(p + '/' + filename)


def is_local():
    if 'http://localhost' in request.host_url:
        return True
    else:
        return False


class MyJSONEncoder(flask.json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            # Convert decimal instances to strings.
            return str(obj)
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        return super(MyJSONEncoder, self).default(obj)
