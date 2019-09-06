from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import logging
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

try: from definitions_prod import *
except Exception as e: pass # Surpass error. Note: Create definitions_prod.py

class GoogleSheet:

    def __init__(self, sheet_id=None, credentials=None, token=None, cred_owner=''):
        self.sheet_id = sheet_id
        self.credentials = credentials
        self.token = token
        self.cred_owner = cred_owner
        self.sheet_metadata = None

    def setup_sheets_api(self):
        SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

        if not os.path.exists(appConfig.GOOGLE_SHEET_CREDENTIALS):
            raise Exception('File %s not exist' % appConfig.GOOGLE_SHEET_CREDENTIALS)

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(appConfig.GOOGLE_SHEET_TOKENS):
            with open(appConfig.GOOGLE_SHEET_TOKENS, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(appConfig.GOOGLE_SHEET_CREDENTIALS, SCOPES)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open(appConfig.GOOGLE_SHEET_TOKENS, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('sheets', 'v4', credentials=creds)

    def call_sheets_api(self, range_name='Sheet1!A1'):
        try:
            RANGE_NAME = range_name
            result = self.service.spreadsheets().values().get(spreadsheetId=self.sheet_id, range=RANGE_NAME).execute()
            values = result.get('values', [])

            extra = 'Credentials owner %s' % self.self.cred_owner() if self.self.cred_owner() else ''
            print('INFO: Read Google Sheet: %s. %s' % (self.get_sheet_url(), extra))

            if not values:
                raise Exception('Empty response from google sheet call_sheets_api')
            else:
                return values
        except Exception as e:
            print(self.get_diagnosis(e))

    def update_sheets_api(self, range='Sheet1!Q1:R1', values=None, notify=False):
        try:
            if not values:
                return False
            if not isinstance(values[0], list):
                raise Exception('Must array 2 dimension')
            body = {'values': values}
            self.service.spreadsheets().values().append(spreadsheetId=self.sheet_id,
                                                        range=range,
                                                        valueInputOption='RAW', body=body).execute()
        except Exception as e:
            print(self.get_diagnosis(e))

        if notify:
            print('\nINFO: Update Google Sheet: %s      %s\n' %  (self.get_sheet_url(), self.get_owner()))

    def get_diagnosis(self, e: Exception = None):
        url = self.get_sheet_url()
        owner = self.get_owner()
        title = self.get_sheet_title()
        tabs = self.get_sheet_tabs()
        msg = '''
            Google URL:     %s
            Sheet Title:    %s   %s
            All tabs name:  %s
        ''' % (url, title, owner, ', '.join(tabs))

        if e:
            err = str(e)
            print('\n\nERROR: ', err)
            if 'Unable to parse range: ' in err:
                err = err.split('Unable to parse range: ')[-1].split('!')[0]
                print('INFO: Please check tab name or range:    ', err)
            if ' 403 ' in err:
                print('INFO: Please check permission of credentials of ', self.get_owner())
        return msg

    def get_sheet_metadata(self):
        if not self.sheet_metadata:
            self.sheet_metadata = self.service.spreadsheets().get(spreadsheetId=self.sheet_id).execute()
        return self.sheet_metadata

    def get_sheet_title(self):
        return self.get_sheet_metadata().get('properties').get('title')

    def get_sheet_tabs(self):
        tabs = []
        for tab in self.get_sheet_metadata().get('sheets'):
            tabs.append(tab.get('properties').get('title'))
        return tabs

    def batch_update_api(self, values=None):
        batch_update_values_request_body = {
            'data': values,
            'value_input_option': 'RAW',
        }
        self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.sheet_id,
                                                         body=batch_update_values_request_body).execute()

    def get_sheet_url(self):
        return 'https://docs.google.com/spreadsheets/d/%s/' % self.sheet_id

    def get_owner(self):
        return self.cred_owner

    def valid_cell_length(self, lst):
        error = False
        for i, row in enumerate(lst):
            for j, cell in enumerate(row):
                if len(cell) > 50000:
                    error = True
                    print('ERROR: Line: %d, column: %d. Have exceed 50000 characters' % (i + 1, j + 1))
        if error:
            raise Exception('Please check character on those cell')


if __name__ == '__main__':
    ''' https://developers.google.com/sheets/api/quickstart/python
        pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
     '''

    g = GoogleSheet('1zR7e6FwkwoPBV5i80qVuQpHEfItUfl3s0Lc8OUs5pHY')
    g.setup_sheets_api()
    # g.update_sheets_api(values=['Updated'])
    import json
    print(json.dumps(g.get_sheet_metadata()))
    print('INFO: Update successful.')
