import logging
from apeeper.extras import TTL, create_iptables_rules, trigger_token, get_process_id, \
						  HTTPAdapterWithSocketOptions, get_additional_details, is_gunicorn

from apeeper.register import get_token_url_from_config, get_list
from flask import Flask,request
import requests
import socket
import sys

app = Flask(__name__)

logger = logging.getLogger('apeeper')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('/tmp/apeeper.log')
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
app.logger.addHandler(handler)
list_items, list = get_list()
CONSOLE_URL=''
CONSOLE_API=''

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if list == 'default':
        alert()
    elif '/../' in request.path:
        alert()
    elif list == 'whitelist':
        do_alert = True
        for item in list_items:
            if request.path.startswith(item):
                do_alert = False
                break
        if do_alert:
            alert()
    elif list == 'blacklist':
        for item in list_items:
            if request.path.startswith(item):
                alert()
                break

    adapter = HTTPAdapterWithSocketOptions(socket_options=[(socket.IPPROTO_IP, socket.IP_TTL, TTL),(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)])
    s = requests.session()
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    resp = s.get('http://'+request.host+request.path)
    return (resp.text, resp.status_code, resp.headers.items())



def alert():
    data = get_additional_details(request)
    trigger_token(url=get_token_url_from_config(), data=data)
