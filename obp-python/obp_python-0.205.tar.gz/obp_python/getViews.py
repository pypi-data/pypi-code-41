import requests
import os
import json
from .init import get_config
from .hasEntitlements import hasEntitlements
from urllib.parse import quote

def getViewsByProvider(bank_id=None, account_id=None, provider=None,
                      provider_id=None):
  """
  Get Account access for User. (The views)
  Returns the list of the views at BANK_ID for account ACCOUNT_ID that a user 
  identified by PROVIDER_ID at their provider PROVIDER has access to.

  Required roles: 
  e.g. obp addrole --role-name <name>
  """

  OBP_AUTH_TOKEN = get_config('OBP_AUTH_TOKEN')
  OBP_API_HOST = get_config('OBP_API_HOST')


  authorization = 'DirectLogin token="{}"'.format(get_config('OBP_AUTH_TOKEN'))
  headers = {'Content-Type': 'application/json',
            'Authorization': authorization}

  url = get_config('OBP_API_HOST') + '/obp/v3.1.0/banks/{bank_id}/accounts/{account_id}/permissions/{provider}/{provider_id}'.format(bank_id=bank_id, account_id=account_id, provider=quote(provider), provider_id=provider_id)
  req = requests.get(url, headers=headers)
  if req.status_code != 200: 
    print("ERROR: Could not get views")
    print(req.text)
    exit(-1)
  elif req.status_code == 200:
    return req


  
