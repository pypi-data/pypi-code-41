import os
import sys
import re
from .loggs import Loggs
from .types import Types

class Options:
    App = None
    Debug = False
    Hosts = []
    Name = None
    Public = False
    Type = None
    Version = None
    Legacy = False
    Logger = Loggs('Options')
    isNats = False
    def __init__(self, app, name, version, hosts, typeMs, public = False, legacy = False, is_nats=False):
        """
            Clase para la construccion de las opciones del microservicio.

            @params app Nombre de la aplicacion
            @params name Nombre del microservicios
            @params version Numero de la version del microservicio
            @params hosts Lista de direcciones de kafka o Nats.
            @params typeMs Tipo del microservicio [WORKER, BIFURCACION]
            @params public Indicador si el servicio es de accesso publico

            @returns void 
        """
        # Validar que se pase la direccion de kafka de forma correcta
        if not isinstance(hosts, list):
            self.Logger.error('No se proporciono una lista de direcciones de kafka correcta')
            sys.exit(-1)
        elif len(hosts) < 1:
            self.Logger.error('Se proporciono una lista vacia de Kafka Hosts')
        
        # Validar que se pase un tipo de microservicio correcto
        if not isinstance(typeMs, Types):
            self.Logger.error('No se proporciono un tipo de microservicio correcto')
            sys.exit(-1)
        
        # Asignar la variable debug a verdadero si no es productivo.
        self.Debug = False if os.environ.get('PRODUCTION', None) else True

        # Asignar el nombre de la aplicacion
        self.App = app

        # Asignar el nombre del microservicio
        self.Name = name

        # Asignar la version
        self.Version = version

        # Asignar el cluster de kafka
        self.Hosts = hosts

        # Asignar el tipo de microservicio
        self.Type = typeMs

        # Asignar el ambito de acceso
        self.Public = public

        # Asignar soporte legado
        self.Legacy = legacy

        # Validar si es Nats
        if os.environ.get('NATS', None) or is_nats:
            self.isNats = True
        elif len(re.findall(r'^nats.*', hosts[0])) > 0:
            self.isNats = True
