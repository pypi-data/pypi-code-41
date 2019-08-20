"""API for sendgrid.

https://sendgrid.com/docs/API_Reference/api_v3.html
"""

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class SendGridAPI(object):
  def __init__(self, api_key):
    self.api_key = api_key

  def send_emails(self,
                  sender_email,
                  sender_name,
                  target_emails,
                  template_id,
                  custom_data={}):
    """Send email to targets.
    """
    targets = [{"email": x} for x in target_emails]
    message = {
        "from": {
            "email": sender_email,
            "name": sender_name
        },
        "personalizations": [{
            "to": targets,
            "dynamic_template_data": custom_data
        }],
        "template_id": template_id
    }
    sg = SendGridAPIClient(self.api_key)
    response = sg.send(message)
    if 200 <= response.status_code < 300:
      return
    else:
      raise Exception(response.body)