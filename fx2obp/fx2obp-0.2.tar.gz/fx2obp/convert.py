import json
import requests
import os
from datetime import datetime
from pathlib import Path
from .fetch_currencies import fetch_currencies


def postFx(POST_TO_OBP=True, WRITE_TO_FILE=False, AUTH_TOKEN=None, 
          API_HOST=None, CURRENCIES=None, sourceDir='./currencies', 
          ephemeral=True, **kwargs):
    """Post all local foreign exchange rates to an OBP instance

    :param POST_TO_OBP: Bool, whether or not to http POST to obp instance 
                        (otherwise will just print to stdout as a dry run).
    :param WRITE_TO_FILE: Bool, whether or not to write post messages to local
                    filesystem. Useful if you want to generate valid OBP
                    fx rate post bodies but not send them to an instance.
    :param AUTH_TOKEN: String, obp api token (also known as Direct Login token)
    :param API_HOST: String The full http/https address of an OBP instance
    :param CURRENCIES: The optional comma seperated list 'gbp,'usd' of 
                       currencies to post, otherwise, all available 
                       currencies will be posted.
    :param sourceDir: String, the directory from which to get fx rates. By default
                   this is "./currencies". Otherwise, give a path from which to
                   read currencies from. E.g. a tmpdir directory returned by
                   :file:`refresh_currencies.py`
    :param ephemeral: Fetch exchange rates intp a tempfile directory and 
                      use these for the post. Don't permanently store fx rates
                      during fetch. Assumes you're starting from scratch and
                      will download all the latest exchange rates for you (and
                      post them into the given API_HOST sandbox).
    """

    if ephemeral and sourceDir != "./currencies":
      print("Passing both ephemeral and sourceDir to postFx is an error")
      print("""If requesting ephemeral, then no sourceDir is needed as
             tmpfile will create, us and (when done) delete itself 
            automatically for you""")
      exit(-1)
  
    if ephemeral:
      fetch_currencies()
   
    # If ephemeral storate is NOT requested, verify the given sourceDir exists
    if ephemeral is not True and not Path.exists(Path(sourceDir)):
      print("Cannot load currencies because Path {} does not exist".format(sourceDir))
      print("""Must load currencies first e.g. using fetch_currencies() and pass the
            directory path to them. By default this is a folder called 'currencies' in 
            your current working directory""")
      exit(-1)

    # If you want to post, set `export POST_TO_OBP=true` before running script
    POST_TO_OBP = os.getenv("POST_TO_OBP", POST_TO_OBP)
    # If you want to write to file, (for example testing) set
    # `export WRITE_TO_FILE=true` before running script
    WRITE_TO_FILE = os.getenv("WRITE_TO_FILE", WRITE_TO_FILE)
    POST_URL = "{}/obp/v3.1.0/banks/{}/fx"
    AUTH_TOKEN = os.getenv("AUTH_TOKEN", AUTH_TOKEN)
    API_HOST = os.getenv("API_HOST", API_HOST)
    CURRENCIES = os.getenv(
        "CURRENCIES", CURRENCIES
    )  # Only get specified currencies: e.g. export CURRENCIES=usd,gbp,dzd

    # Get bank ids
    req = requests.get(
        API_HOST + "/obp/v3.1.0/banks", headers={"Content-Type": "Application/Json"}
    )
    if req.status_code != 200:
        print(req)
    banks = json.loads(req.text)["banks"]

    """
  For each file input , convert it to an OBP foriegn exchange valid payload.
  Populate for each bank.

  Required roles:
  - CanCreateFxRate
  - CanCreateFxRateAtAnyBank

  Valid example:
  {
    "bank_id":"bankid123",
    "from_currency_code":"EUR",
    "to_currency_code":"USD",
    "conversion_value":1.0,
    "inverse_conversion_value":1.0,
    "effective_date":"2017-09-19T00:00:00Z"
  }
  Invalid format example from source: (http://www.floatrates.com)
  "usd": {
    "code": "USD",
    "alphaCode": "USD",
    "numericCode": "840",
    "name": "U.S. Dollar",
    "rate": 1.0001337101383,
    "date": "Wed, 20 Mar 2019 12:00:02 GMT",
    "inverseRate": 0.9998663077377
  }
  """

    def post_currency(fh):
        data = fh.read()
        src_currency = (
            str(currency_file.resolve()).split("currencies/")[1].split(".json")[0]
        )
        if data == "":
            return -1
        currencies = json.loads(data)

        for to_currency_code, value in currencies.items():
            output = {}
            output["from_currency_code"] = str(src_currency.upper())
            output["to_currency_code"] = str(to_currency_code.upper())
            output["conversion_value"] = value["rate"]
            output["inverse_conversion_value"] = value["inverseRate"]
            src_date = currencies[to_currency_code]["date"]
            src_date_format = "%a, %d %b %Y %H:%M:%S %Z"
            date = datetime.strptime(src_date, src_date_format)
            dst_date_format = "%Y-%m-%dT%k:%M:%S%ZZ"
            output["effective_date"] = date.strftime(dst_date_format)
            # For every bank, generate and write out the same exchange rate
            for bank in banks:
                output["bank_id"] = bank["id"]
                if str(POST_TO_OBP).lower() == "true":
                    url = POST_URL.format(API_HOST, bank["id"])
                    authorization = 'DirectLogin token="{}"'.format(AUTH_TOKEN)
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": authorization,
                    }
                    request = requests.put(
                        url, headers=headers, data=json.dumps(output)
                    )
                    print(request.text)
                if str(WRITE_TO_FILE).lower() == "true":
                    with open(
                        bank["id"]
                        + "-"
                        + src_currency
                        + "-"
                        + to_currency_code
                        + "-obp.json",
                        "w",
                    ) as fp_output:
                        fp_output.write(json.dumps(output))
        fh.close()

    if CURRENCIES:
        currency_codes = CURRENCIES.split(",")
        for currency in currency_codes:
            currency_file = Path(sourceDir, "/{}.json".format(currency.lower()))
            with open(currency_file) as fh:
                post_currency(fh)
    else:
        for currency_file in Path(sourceDir).iterdir():
            with open(currency_file) as fh:
                post_currency(fh)
