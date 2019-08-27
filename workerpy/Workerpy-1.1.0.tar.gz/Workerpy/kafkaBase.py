import base64
import json
import sys
from kafka import KafkaConsumer, KafkaProducer, KafkaAdminClient
from .loggs import Loggs

class KafkaBase:
    """
        Base del microservicio que se aplica para
        la comunicacion con kafka
    """
    # Topico de conexion
    __TOPIC = ''
    # Direccion de kafka
    __KAFKAHOSTS = ''
    # Instancia del consumer
    __CONSUMER = None
    # Instancia del producer
    __PRODUCER = None
    # Nombre del grupo
    __NAME = None
    # Logs de la aplicacion
    logs = Loggs('Core')

    def __init__(self, name, topic, kafkaHosts):
        # Asignar el topico de conexion
        self.__TOPIC = topic
        # Asignar el nombre del worker group
        self.__NAME = name
        # Asginar el hosts de kafka 
        self.__KAFKAHOSTS = kafkaHosts
        # Conectar a Kafka Consumer
        self.__connectConsumer()

    def __connectConsumer(self):
        """
            Metodo para realizar la conexion al cosumer de kafka.
        """
        # Conexion a kafka
        try:
            self.__CONSUMER = KafkaConsumer(
                self.__TOPIC,
                group_id=self.__NAME, # Para la replicacion
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                bootstrap_servers=self.__KAFKAHOSTS,
                value_deserializer=self.__b64_to_json
            )
        except:
            self.logs.error('Ocurrio un error al conectar con Kafka')
            sys.exit(-1)

        # Notificar que se encuentra conectado
        self.logs.info("Escuchando el topico {} en el Kafka {}".format(self.__TOPIC, ','.join(self.__KAFKAHOSTS)))

        # Escuchar todos los posibles eventos
        for msg in self.__CONSUMER:
            self._message(msg.value)

    def _message(self, msg):
        """
            Metodo para el procesamiento de mensajes de
            kafka.
        """
        pass

    def __b64_to_json(self,encoded):
        """
            Metodo que conviernte un base64 a dict
        """
        decoded = base64.b64decode(encoded)
        return json.loads(decoded.decode('utf-8'))

    def _send(self, topico, msj, idTransaction):
        """
            Metodo para el envio de datos a Kafka

            @params topico Topico en el que se publica
            @params msj Mensaje que enviara
            @params idTransaction Id de la transaccion
        """
        try:
            self.__PRODUCER.send(topico, key=str.encode(str(idTransaction)), value=msj)
        except Exception as e:
            self.logs.error(e)
            sys.exit(-1)
        