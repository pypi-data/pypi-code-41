QUERY_SERVER = "https://cleverlab-api-bridge.eu-de.mybluemix.net"
QUERY_ENDPOINT = "/demo"
QUERY_SERVER_PORT = "443"


import common_pb2 as common
from loader import DeviceDescriptor     

import requests

def serializeMessage(message):
    return message.SerializeToString()

def deserializeMessage(toMessage, data):
    toMessage.ParseFromString(data)
    return toMessage

def makeRequest(accessToken, deviceDescriptor, requestMessage):
    

    request = common.ClientQuery()
    request.Devicevendorurl = deviceDescriptor.getVendorURL()
    request.Devicetype = deviceDescriptor.getDeviceType()
    request.Devicefeatureid = requestMessage.DESCRIPTOR.name
    request.Arugments = serializeMessage(requestMessage)

    body = serializeMessage(request)

    resp = requests.post(QUERY_SERVER + QUERY_ENDPOINT + "/query", \
        headers={"content-type": "application/protobuf", "authorization": accessToken},\
        data=body, )

    if resp.status_code == 200:
        # unpack result
        cleverlabResponse = common.Response()
        deserializeMessage(cleverlabResponse, resp.content)

        if cleverlabResponse.Error == common.Response.ResultType.NO_ERROR:
            return cleverlabResponse.Result

        elif cleverlabResponse.Error == common.Response.ResultType.NO_ERROR_WITH_PROMISE:
            raise NotImplementedError("http client doesn't supports promise currently")
        else:
            raise ValueError("request failed with error code=" + str(cleverlabResponse.Error))

    else:
        raise IOError("request failed with code=" + str(resp.status_code) + " : " + (resp.content.decode("utf-8") ))

import login_pb2 as login  

class AccessManager:
    def __init__(self, username, password):
        self._username = username
        self._password = password

    def login(self):
        
        # login
        loginRequest = login.LoginRequest()
        loginRequest.Username = self._username
        loginRequest.Password = self._password 

        resp = requests.post(QUERY_SERVER + QUERY_ENDPOINT + "/login", \
            headers={"content-type": "application/protobuf"}, \
            data=serializeMessage(loginRequest))

        loginResponse = login.LoginResponse()
        if resp.status_code == 401:
            return False, "logged failed"
        elif resp.status_code == 404:
            return False, "desired device not found or not authorized to you"
        elif resp.status_code != 200:
            return False, "unexpected error, request failed with status=" + str(resp.status_code)
        else:
            loginResult = deserializeMessage(loginResponse, resp.content)
            self._token = loginResult.Token
            return True, self._token

    def changePassword(self, newPassword):
        # changepassword
        self._newPassword = newPassword

        changePasswordRequest = login.ChangePasswordRequest()
        changePasswordRequest.Token = self._token
        changePasswordRequest.Oldpassword = self._password
        changePasswordRequest.Newpassword = newPassword

        resp = requests.post(QUERY_SERVER + QUERY_ENDPOINT + "/changePassword", \
            headers={"content-type": "application/protobuf", "authorization": self._token}, \
            data=serializeMessage(changePasswordRequest))

        if resp.status_code == 401:
            return False, "not logged in"
        elif resp.status_code != 200:
            return False, "unexpected error, request failed with status=" + str(resp.status_code)
        else:
            return True, ""

    def logout(self):
        # logout
        
        logoutRequest = login.LogoutRequest()
        logoutRequest.Token = self._token

        resp = requests.post(QUERY_SERVER + QUERY_ENDPOINT + "/logout", \
            headers={"content-type": "application/protobuf", "authorization": self._token}, \
            data=serializeMessage(logoutRequest))

        if resp.status_code == 401:
            return False, "not logged in"
        elif resp.status_code != 200:
            return False, "unexpected error, request failed with status=" + str(resp.status_code)
        else:
            return True, ""
