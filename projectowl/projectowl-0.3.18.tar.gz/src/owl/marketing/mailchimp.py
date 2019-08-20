"""Script to use mailchimp api.
"""

import requests


class MailchimpAPI(object):
  """Class to manage mailchimp api.
  """
  ROOT_API = "https://us16.api.mailchimp.com/3.0"

  def __init__(self, api_key):
    """Init with api key.
    """
    self.api_key = api_key
    self.auth_option = ("anyuser", self.api_key)

  def get_lists(self):
    """Retrieve all lists.
    """
    res = requests.get("{}/lists".format(self.ROOT_API), auth=self.auth_option)
    res.raise_for_status()
    res_data = res.json()
    assert res_data["status"]

  def get_list(self, list_id):
    """Get contact info from list.
    """
    res = requests.get(
        "{}/lists/{}".format(self.ROOT_API, list_id), auth=self.auth_option)
    res.raise_for_status()
    res_data = res.json()
    print(res_data)

  def get_list_members(self, list_id, only_email=True):
    """Get member info from a list.
    """
    res = requests.get(
        "{}/lists/{}/members?count=300".format(self.ROOT_API, list_id),
        auth=self.auth_option)
    res.raise_for_status()
    res_data = res.json()
    if only_email:
      emails = []
      for member in res_data["members"]:
        emails.append(member["email_address"])
      return emails
    else:
      return res_data["members"]
