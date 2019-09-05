from pprint import pprint
import pika
import os
import json
import time
import threading

class Work_Queue_Task_Server():

    import pika
import uuid
import os
import json
from pprint import pprint

class Work_Queue_Task_Client():

    def __init__(self, queue_name = None):
        
        url = os.environ.get('CLOUDAMQP_URL', 'amqp://tvmjkfee:0BCkrC2idZZJcrCSCXDsoVpd1_VWisUh@emu.rmq.cloudamqp.com/tvmjkfee')
        params = pika.URLParameters(url)

        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.queue_name = queue_name 
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def send (self,journal):

        self.channel.basic_publish(
                exchange='topic_seon', 
                routing_key=self.queue_name, 
                 properties=pika.BasicProperties(
                     content_type = "application/json",
                     delivery_mode=2),  
                body=json.dumps(journal.__dict__))

        self.connection.close()
  
        

        

        

        







