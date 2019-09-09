import os
import json
import requests as req
from yellow_idea_py.mysql import MySqlDatabase

db = MySqlDatabase(
    host=os.environ['DB_HOST'],
    user=os.environ['DB_USER'],
    passwd=os.environ['DB_PASSWORD'],
    database=os.environ['DB_DATABASE']
)

line_endpoint = 'https://api.line.me'


class Line:

    def create(self, payload):
        payload['line_display_name'] = payload['line_display_name'].replace("'", "")
        return db.do_insert('master_user_line', payload)

    def profile(self, line_user_id):
        query = f"SELECT * FROM master_user_line WHERE id = '{line_user_id}'"
        data = db.do_fetch(query)
        return data[0]

    def count_user(self, line_user_id):
        query = f"SELECT id FROM master_user_line WHERE line_user_id = '{line_user_id}'"
        data = db.do_fetch(query)
        if len(data) > 0:
            return data[0]
        else:
            return None

    def token(self, code, chanel_detail, callback_url):
        chanel_id = chanel_detail['chanel_id']
        client_secret = chanel_detail['chanel_secret']
        url = f"{line_endpoint}/oauth2/v2.1/token"
        payload = f"grant_type=authorization_code" \
                  f"&code={code}" \
                  f"&redirect_uri={callback_url}" \
                  f"&client_id={chanel_id}" \
                  f"&client_secret={client_secret}"
        headers = {
            'Content-Type': "application/x-www-form-urlencoded"
        }
        response = req.request("POST", url, data=payload, headers=headers)
        return json.loads(response.text)

    def access_token(self, access_token):
        url = f"{line_endpoint}/oauth2/v2.1/verify?access_token={access_token}"
        response = req.request("GET", url)
        return json.loads(response.text)


class Chanel:

    def detail(self):
        return {
            'chanel_id': str(os.environ['LINE_CHANEL_ID']),
            'chanel_secret': os.environ['LINE_CHANEL_SECRET']
        }


class Message:

    def __init__(self):
        self.channel_access_token = self.get_channel_access_token()

    def get_channel_access_token(self):
        return os.environ['LINE_CHANEL_ACCESS_TOKEN']

    def push_message(self, line_user_id, messages):
        url = f"{line_endpoint}/v2/bot/message/push"
        payload = {
            "to": line_user_id,
            "messages": messages
        }
        headers = {
            'Content-Type': "application/json",
            'Authorization': f"Bearer {self.channel_access_token}",
        }
        try:
            response = req.request("POST", url, data=json.dumps(payload), headers=headers)
            print(response.text)
            # return json.loads(response.status_code)
            return True
        except:
            print("Push Message Fail")
            return False
