"""
Elipse Plant Manager - EPM Web API
Copyright (C) 2018 Elipse Software.
Distributed under the MIT License.
(See accompanying file LICENSE.txt or copy at http://opensource.org/licenses/MIT)
"""

import datetime as dt
import requests
import json
from .autostarttimer import AutoStartTimer

class AuthorizationService(object):

  def __init__(self, authServer, clientId, programId, userName, password):
    self._authServer = authServer
    self._clientId = clientId
    self._programId = programId
    self._userName = userName
    self._password = password
    self._refreshToken = None
    self._tokenExpiration = None
    self._token = None
    self._token = self.renewToken()
    self._timer = AutoStartTimer(180, self.reloadToken)
    self._error = ''

  def reloadToken(self):
    try:
      self._token = self.renewToken()
      self._error = ''
    except Exception as ex:
      self._token = ''
      self._error = str(ex)
    
  def renewToken(self):
    if (self._token != None):
      return self.refreshToken()

    client_auth = requests.auth.HTTPBasicAuth(self._clientId, self._programId)
    post_data = {"grant_type": "password", 
                  "username": self._userName,
                  "password": self._password,
                  "scope": "offline_access openid profile email opcua_browse opcua_read opcua_write opcua_subscription opcua_history EpmWebApi portal_files portal_upload"} #EpmProcessor #openid profile email opcua_browse opcua_read opcua_subscription 
    auth_url = self._authServer + '/connect/token'
    response = requests.post(auth_url,
                             auth=client_auth,
                             data=post_data, verify=False)
    respose_json = response.json()

    if response.status_code != 200:
        raise Exception("GetToken() call http error '" +  str(response.status_code) + "'. Reason: " + respose_json["error"])

    self._refreshToken = respose_json["refresh_token"]

    return respose_json["access_token"]

  def getToken(self):
    if self._error == '':
      return self._token
    else:
      raise Exception(self._error)

  def refreshToken(self):
    client_auth = requests.auth.HTTPBasicAuth(self._clientId, self._programId)
    post_data = {"grant_type": "refresh_token", 
                 "refresh_token": "%s"%(self._refreshToken) }
    auth_url = self._authServer + '/connect/token'
    response = requests.post(auth_url,
                              auth=client_auth,
                              data=post_data, verify=False) 
    respose_json = response.json()

    if response.status_code != 200:
        raise Exception("RefreshToken() call http error '" +  str(response.status_code) + "'. Reason: " + respose_json["error"])

    
    self._refreshToken = respose_json["refresh_token"]
    return respose_json["access_token"]

  def logout(self):
    if (self._token == None):
      return
    post_data = { "token" : self._token }
    client_auth = requests.auth.HTTPBasicAuth(self._clientId, self._programId)
    auth_url = self._authServer + '/connect/revocation'
    response = requests.post(auth_url,
                              auth=client_auth,
                              data=post_data, verify=False)
    if (self._refreshToken == None):
      return
    post_data = { "token" : self._refreshToken, "token_type_hint" : "refresh_token" }
    client_auth = requests.auth.HTTPBasicAuth(self._clientId, self._programId)
    auth_url = self._authServer + '/connect/revocation'
    response = requests.post(auth_url,
                              auth=client_auth,
                              data=post_data, verify=False)

  def close(self):
    try:
      self._timer.cancel()
    except Exception as ex:
      import logging
      logging.exception(ex)
    self.logout()

  def restart(self):
    self._refreshToken = None
    self._tokenExpiration = None
    self._token = None
    self._token = self.renewToken()
    self._timer = AutoStartTimer(60, self.reloadToken)



