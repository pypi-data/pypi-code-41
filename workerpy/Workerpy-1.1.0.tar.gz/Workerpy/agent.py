"""
    Clase que contiene la logica de un agente
    para poder responder a las diferentes acciones
    que se le aplican.
"""
import sys
import os
import asyncio
import inspect
import json
import socket
import uuid
import datetime
from abc import ABCMeta, abstractmethod # OPP

if os.environ.get('KAFKA', None):
    from .kafkaBase import KafkaBase as BaseClass
elif os.environ.get('NATS', None):
    from .NatsBase import NatsBase as BaseClass
else:
    # En caso que se no indique por variable de entorno
    from .kafkaBase import KafkaBase as BaseClass

from .options import Options

class Worker(BaseClass, metaclass=ABCMeta):

    # Acciones del microservicio
    __ACTIONS = {}

    def __init__(self, opt):
        # Validar que se pase un objeto de configuracion correcto
        if not isinstance(opt, Options):
            self.logs.error('No se proporciono una configuracion correcta')
            sys.exit(-1)

        # llamar el constructor padre
        BaseClass.__init__(self, opt.Name, opt.Topic, opt.Kafka)

        # Ver si es utilizado sobre NATS
        if not os.environ.get('NATS', None) is None:
            # iniciar la aplicacion
            self.loop = asyncio.get_event_loop()
            self.loop.run_until_complete(self.run())
            try:
                self.loop.run_forever()
            finally:
                self.loop.close()
    
    def _message(self, msg):
        """
            Metodo para capturar los datos del mensaje
        """
        # Enviar al elemento que los procesa
        self.process(msg)
    
    @abstractmethod
    def process(self, data):
        pass
