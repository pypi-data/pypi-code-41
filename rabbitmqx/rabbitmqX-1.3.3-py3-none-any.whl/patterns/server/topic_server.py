from pprint import pprint
import pika
import os
import json
import time

class Topic_Server():

    def __init__(self, binding_key, integration_service):
        
        self.url = os.environ.get('CLOUDAMQP_URL', 'amqp://tvmjkfee:0BCkrC2idZZJcrCSCXDsoVpd1_VWisUh@emu.rmq.cloudamqp.com/tvmjkfee')
        self.params = pika.URLParameters(self.url)
        self.connection = pika.BlockingConnection(self.params)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='topic_seon', exchange_type='topic')
        
        self.result = self.channel.queue_declare('', exclusive=True)
        
        self.queue_name = self.result.method.queue
        self.integration_service = integration_service
        
        self.channel.queue_bind(exchange='topic_seon', queue=self.queue_name, routing_key=binding_key)
    
            
    def callback(self,ch, method, properties, body):
            
        data = json.loads(body)
        return self.integration_service(data)
        #loop = asyncio.new_event_loop()
        #loop.run_until_complete(self.do(data))
        #loop.close()
        
    #def do (self, data):
     #    asyncio.ensure_future(self.integration_service(data))
    
    
    def start(self):

        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=self.callback, auto_ack=True)
        
        time.sleep(2)
        self.channel.start_consuming()
        

        

        

        

        







