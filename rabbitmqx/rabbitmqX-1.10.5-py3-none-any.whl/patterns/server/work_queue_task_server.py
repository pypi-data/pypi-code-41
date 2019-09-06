from pprint import pprint
import pika
import os
import json
import time
import threading

class Work_Queue_Task_Server():

    def run(self):

        self.url = os.environ.get('CLOUDAMQP_URL', 'amqp://tvmjkfee:0BCkrC2idZZJcrCSCXDsoVpd1_VWisUh@emu.rmq.cloudamqp.com/tvmjkfee')
        self.params = pika.URLParameters(self.url)
        self.connection = pika.BlockingConnection(self.params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)
        
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=self.callback)
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()

    def __init__(self, queue_name, integration_service):

        self.queue_name = queue_name
        self.integration_service = integration_service
        
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True 
        thread.start() 
            
    def callback(self,ch, method, properties, body):
        
        data = json.loads(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return self.integration_service.do(data)
    
    def close(self):
        self.connection.close()
        
       
        

        

        

        







