from googleapiclient import sample_tools
from googleapiclient.http import build_http

try: from definitions_prod import *
except Exception as e: pass # Surpass error. Note: Create definitions_prod.py
from swissarmykit.utils.fileutils import FileUtils

discovery_doc = appConfig.CONFIG_PATH + "/credentials/mybusiness_google_rest_v4p4.json"

def main(argv):
    # Use the discovery doc to build a service that we can use to make
    # MyBusiness API calls, and authenticate the user so we can access their
    # account
    service, flags = sample_tools.init(argv, "mybusiness", "v4", __doc__, __file__, scope="https://www.googleapis.com/auth/business.manage", discovery_filename=discovery_doc)

    # Get the list of accounts the authenticated user has access to
    output = service.accounts().list().execute()
    print("List of Accounts:\n")
    print(json.dumps(output, indent=2) + "\n")

    firstAccount = output["accounts"][0]["name"]

    # Get the list of locations for the first account in the list
    print("List of Locations for Account " + firstAccount)
    locationsList = service.accounts().locations().list(parent=firstAccount).execute()
    print(json.dumps(locationsList, indent=2))

if __name__ == "__main__":
  main('h')