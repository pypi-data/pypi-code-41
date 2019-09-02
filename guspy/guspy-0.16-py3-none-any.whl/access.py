from simple_salesforce import Salesforce, SalesforceLogin
import pandas as pd


class Gus:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.soql = self.connect()

    def get_instance(self):
        try:
            session_id, instance = SalesforceLogin(username=self.username,
                                                   password=self.password)
            gus = dict(session_id=session_id, instance=instance, error=None)
        except Exception as e:
            gus = dict(error=e)
        return gus

    def connect(self):
        gus = self.get_instance()
        if not gus['error']:
            return Salesforce(session_id=gus['session_id'],
                              instance=gus['instance'])
        else:
            return gus['error']

    def raw(self, query):
        try:
            data = self.soql.query_all(query)['records']
            return data
        except Exception as e:
            return str(self.soql)

    def parse(self, query):
        data = self.raw(query)
        try:
            data = pd.DataFrame(data)
            if data.empty:
                pass
            else:
                data = data.drop('attributes', axis=1)
        except:
            pass
        return data
