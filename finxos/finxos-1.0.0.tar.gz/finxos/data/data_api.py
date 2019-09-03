# encoding: UTF-8

import json
import pandas as pd
from . import rest_agent


class FDataApi(object):
    def __init__(self, addr):
        """Create FDataApi client.
        """
        self._addr = addr
        self._username = ""
        self._password = ""
        self._token = ""
        self._timeout = ""
        self._agent = rest_agent.RestAgent()

    def set_timeout(self, timeout):
        self._timeout = timeout

    def login(self, username, password):
        self._username = username
        self._password = password
        return self._do_login()

    def _do_login(self):
        if self._username and self._password:
            params = {"phone": self._username, "passwd": self._password}

            url = "https://%s/apiv1/instweb/instadmin/signin/passwd" % self._addr
            response = self._agent.do_request(url, params, method="POST")
            if response is not None:
                jsonobj = json.loads(response)
                code = jsonobj["code"]
                message = jsonobj["message"]

                if code != 20000 :
                    return False, "%d,%s" % (code, message)
                else:
                    self._token = jsonobj["data"]["token"]
                    self._agent.add_headers({"X-Tu-Token" : self._token})
                    return True, ""
        else:
            self._token = ""
            return False, "empty username or password"

    # the following functions are for data api
    def get_api_list(self, api_type=""):
        if self._token == "":
            return None, "please login first"

        url = "https://%s/apiv1/tucloud/data/get_api_list" % self._addr
        params = {"api_type" : api_type}
        response = self._agent.do_request(url, params, method="POST")
        if response is not None:
            jsonobj = json.loads(response)
            code = jsonobj["code"]
            message = jsonobj["message"]

            if code != 20000:
                return False, "%d,%s" % (code, message)
            else:
                api_list = jsonobj["data"]["api_list"]
                return pd.DataFrame(api_list), ""
        else:
            return None, "http error [%s]" % url

    def get_api_param(self, api_id, param_type):
        if self._token == "":
            return None, "please login first"

        url = "https://%s/apiv1/tucloud/data/get_api_param" % self._addr
        params = {"api_id": api_id, "param_type" : param_type}
        response = self._agent.do_request(url, params, method="POST")
        if response is not None:
            jsonobj = json.loads(response)
            code = jsonobj["code"]
            message = jsonobj["message"]

            if code != 20000:
                return False, "%d,%s" % (code, message)
            else:
                api_param = jsonobj["data"]["api_param"]
                return pd.DataFrame(api_param), ""
        else:
            return None, "http error [%s]" % url

    def query_data(self, api_id, filters="", fields=""):
        if self._token == "":
            return None, "please login first"

        url = "https://%s/apiv1/tucloud/data/query_data" % self._addr
        params = {"api_id": api_id, "filters" : filters, "fields" : fields}
        response = self._agent.do_request(url, params, method="POST")
        if response is not None:
            jsonobj = json.loads(response)
            code = jsonobj["code"]
            message = jsonobj["message"]

            if code != 20000:
                return False, "%d,%s" % (code, message)
            else:
                columns = jsonobj["data"]["columns"]
                value = jsonobj["data"]["value"]
                df = pd.DataFrame(value).T
                df.columns = columns
                return df, ""
        else:
            return None, "http error [%s]" % url

