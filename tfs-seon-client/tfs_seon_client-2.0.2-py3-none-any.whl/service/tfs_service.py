import pika
import uuid
import os
import json
from pprint import pprint
from rabbitmqX.patterns.client.rpc_client import RPC_Client
from rabbitmqX.journal.journal import Journal
import json 
class TFS_Service (RPC_Client):
    
    def __init__(self, type):
        RPC_Client.__init__(self,'integration.tfs')
        self.type = type

    def integrate(self, organization_id):

        data = {'organization_id': organization_id}       
        journal = Journal(self.type,data,"integration")
        response = self.do(journal.__dict__)
        return json.loads(response)

