import requests
from .init import get_config
import sys, traceback
from .hasEntitlements import hasEntitlements

#Delete view( CanDeleteCardsForBank) 

def deleteViewById(bank_id, account_id, view_id):
  OBP_AUTH_TOKEN = get_config('OBP_AUTH_TOKEN')
  OBP_API_HOST = get_config('OBP_API_HOST')

  # Validate entitlements
  requiredEntitlements = []
  fail, msg = hasEntitlements(entitlements_required=requiredEntitlements)

  if fail is True:
    print(msg)
    exit(-1)

  url = get_config('OBP_API_HOST') + '/obp/v3.1.0/banks/{bank_id}/accounts/{account_id}/views/{view_id}'.format(bank_id=bank_id,
account_id=account_id, view_id=view_id)

  authorization = 'DirectLogin token="{}"'.format(get_config('OBP_AUTH_TOKEN'))
  headers = {'Content-Type': 'application/json',
            'Authorization': authorization}
  req = requests.delete(url, headers=headers)

  if req.status_code == 403:
    print(req.text)
    exit(-1)

  return req
