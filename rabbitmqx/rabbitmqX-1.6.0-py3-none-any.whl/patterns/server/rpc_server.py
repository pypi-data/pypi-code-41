
from pprint import pprint
import pika
import os
import json
import threading

class RPC_Server(object):


    def run(self):

        self.url = os.environ.get('CLOUDAMQP_URL', 'amqp://tvmjkfee:0BCkrC2idZZJcrCSCXDsoVpd1_VWisUh@emu.rmq.cloudamqp.com/tvmjkfee')
        self.params = pika.URLParameters(self.url)
        self.connection = pika.BlockingConnection(self.params)

        self.channel = self.connection.channel()
        
        self.channel.queue_declare(queue=self.queue_name)

        self.channel.basic_qos(prefetch_count=1)

        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.on_request)
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()

        self.connection.close()
        

    def __init__(self, queue_name, integration_service):
        
        pprint ("|--> "+queue_name)
        self.queue_name = queue_name
        self.integration_service = integration_service

        thread = threading.Thread(target=self.run)
        #thread.daemon = True 
        thread.start()  
        
    
    def on_request(self,ch, method, props, body):

        data = json.loads(body)

        self.integration_service.do(data)

        ch.basic_publish(exchange='',
                            routing_key=props.reply_to,
                            properties=pika.BasicProperties(correlation_id = \
                                                                props.correlation_id,
                                                                content_type = "application/json"))
            
        ch.basic_ack(delivery_tag = method.delivery_tag)
        
        
    