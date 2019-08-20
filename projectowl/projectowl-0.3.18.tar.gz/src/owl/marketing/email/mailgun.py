"""Mailgun API.
"""

import requests


class MailgunAPI(object):
  ROOT_API = "https://api.mailgun.net/v3/sandbox6762079c5f8a4e9cbdf033962d138e3b.mailgun.org"

  def __init__(self, api_key):
    self.api_key = api_key

  def send_emails(self, sender, targets):
    """Send emails to targets.
    """
    res = requests.post(
        "{}/messages".format(self.ROOT_API),
        auth=("api", self.api_key),
        data={
            "from": sender,
            "to": targets,
            "subject": "Hello",
            "text": "Testing some Mailgun awesomness!"
        })
    res_data = res.json()
    print(res_data)
