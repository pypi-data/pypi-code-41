# -*- coding: utf-8 -*-
import json

from flask import Flask, request, jsonify
import socket
from univider.settings import app_user
from univider.logger import Logger
import cx_Oracle

app = Flask(__name__)
logger = Logger(__name__).getlogger()

db_conn = cx_Oracle.connect('spd_dm/spd_dm_1Q#@pdb_spider')
oreader = db_conn.cursor()

@app.route("/crawl", methods=['GET', 'POST'])
def crawl():
    # parse needs
    data = request.get_data()
    params = json.loads(data)
    node = socket.gethostname()
    # authentication
    if (params.has_key("user") and params.has_key("secret") and params["secret"] == app_user.get(params["user"])):
        # handle needs
        from univider.fetcher import Fetcher
        fetcher = Fetcher()
        result = fetcher.fetch_page_with_cache(params,oreader)
    else:
        if (params.has_key("user")):
            logger.info(params["user"] + ' Authentication failed ' )
        else:
            logger.info('Unknown user Authentication failed '+str(params))
        result = {
            'status': 'error',
            'node' : node,
            'description': 'Authentication failed.'
        }

    # return needs
    return jsonify(result)
    # return result["html"].decode('gbk')

@app.route('/get_ip_list', methods=['POST','GET'])
def get_ip_list():
    results = []
    sql = "select * from ip_pool_all"
    #print sql
    oreader.execute(sql)
    result = oreader.fetchall()
    for each in result:
        row = {}
        row['ip'] = each[0]
        row['time'] = each[1]
        results.append(row)
    return jsonify(results)


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5010,debug=False)
def main():
    app.run(host='0.0.0.0',port=5010,debug=False)