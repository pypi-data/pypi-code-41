import os
import sys
from .loggs import Loggs

class Options:
    Debug = False
    Kafka = []
    Name = None
    Topic = None
    Logger = Loggs('Options')
    def __init__(self, name, topic, kafka):
        """
            Clase para la construccion de las opciones del microservicio.

            @params name Nombre del Worker
            @params topic Nombre del topico
            @params kafka Lista de direcciones de kafka.

            @returns void 
        """
        # Validar que se pase la direccion de kafka de forma correcta
        if not isinstance(kafka, list):
            self.Logger.error('No se proporciono una lista de direcciones de kafka correcta')
            sys.exit(-1)
        elif len(kafka) < 1:
            self.Logger.error('Se proporciono una lista vacia de Kafka Hosts')

        
        # Asignar la variable debug a verdadero si no es productivo.
        self.Debug = False if os.environ.get('PRODUCTION', None) else True

        # Asignar el topico de conexion
        self.Topic = topic

        # Asignar el nombre del worker
        self.Name = name

        # Asignar el cluster de kafka
        self.Kafka = kafka
