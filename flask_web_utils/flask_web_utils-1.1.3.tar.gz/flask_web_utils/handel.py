from flask_cors import CORS
import json
from flask import Flask, request, Response
import traceback

app = Flask(__name__, static_folder='', static_url_path='')
CORS(app, resources=r'/*')


def get_args(request, myargs):
    status = 200
    args =[]
    try:
        if request.method == "POST":
            if request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
                args = [request.form.get(arg) for arg in myargs]
            elif request.headers['Content-Type'] == 'application/json':
                json_data = request.get_json().items()
                args = [json_data[arg] for arg in myargs]
            else:
                assert False
        else:
            args = [request.args.get[arg] for arg in myargs]
    except:
        status = 400
        traceback.print_exc()
    return status, args


def run_server(port):
    app.run(host='0.0.0.0', port=port)


# @app.route('/getvec', methods=['GET', 'POST'])
# [sys.argv[2] for i in range(arg_len)]
def excemple():
    args = ['text', 'word']
    status, myargs = get_args(request, args)
    # .................
    result = ''
    return Response(json.dumps(result), status=status, mimetype='application/json')
