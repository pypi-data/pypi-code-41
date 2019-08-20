import pika
import uuid
import os
import json
from pprint import pprint
from rabbitmqX.patterns.client.rpc_client import RPC_Client
from rabbitmqX.journal.journal import Journal

class Clockify_Service(RPC_Client):
    
    def __init__(self, type):

        RPC_Client.__init__(self,'integration.clockify')
        
        self.type = type

    def integrate(self, organization_id = None, seon_entity_id = None, seon_entity_as_workspace = None):
        
        data = {'organization_id': organization_id,
                'seon_entity_id': seon_entity_id,
                'seon_entity_as_workspace': seon_entity_as_workspace}       
        journal = Journal(self.type,data,"integration_with")

        return self.do(journal.__dict__)
