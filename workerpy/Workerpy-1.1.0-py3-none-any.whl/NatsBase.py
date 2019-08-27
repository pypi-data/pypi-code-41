import asyncio
import base64
import json
import sys
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers
from .loggs import Loggs

class NatsBase:

    # Instancia de Nats Client
    __nc = NATS()

    # Logs de la aplicacion
    logs = Loggs('Core')

    # Nombre del agente     
    __Name = ''

    # Hots De Nats
    __Nats_Host = ''

    # Indicar si es un cola de procesos
    __isQueue = False

    # Nombre del cliente
    __name = None

    # Loop de la aplicacion
    loop = None

    # Topico que se escueha
    __Topic = None

    # Init
    def __init__(self, name, topic, NatsHosts, Queue = True):
        self.__Name = name
        self.__Nats_Host = NatsHosts
        self.__isQueue = Queue
        self.__name = name
        self.__Topic = topic

    async def run(self):
        # Servidores
        servers = []

        # Dar el formato correcto
        for ntServer in self.__Nats_Host:
            servers.append('nats://{}'.format(ntServer))

        # Setup pool of servers from a NATS cluster.
        options = {
            "servers": servers,
            "io_loop": asyncio.get_running_loop(),
            "name": self.__name,
            'dont_randomize': True,
            'max_reconnect_attempts': 5,
            'reconnect_time_wait': 2,
            "disconnected_cb": self.disconnected_cb,
            "reconnected_cb": self.reconnected_cb,
            "error_cb": self.error_cb,
            "closed_cb": self.closed_cb
        }

        # Connect
        try:
            await self.__nc.connect(**options)
        except ErrNoServers as e:
            # Could not connect to any server in the cluster.
            print(e)
            sys.exit(-1)

        # Validar que se haya establecido una conexion
        if self.__nc.is_connected:
            # Conectar y escuchar el evento del metodo unico
            if self.__isQueue:
                await self.__nc.subscribe(self.__Topic, queue=self.__Name, cb=self.subscribe_handler)
            else:
                await self.__nc.subscribe(self.__Topic, cb=self.subscribe_handler)
            self.logs.info('Conexion establecida con el servidor de NATS: {}'.format(self.__Nats_Host))

        err = self.__nc.last_error
        if err is not None:
            self.logs.info("Ocurrio un error: {}".format(err))
    
    @asyncio.coroutine
    async def disconnected_cb(self):
        self.logs.warning("Se realizo una desconexion de NATS: {}".format(self.__Nats_Host))
    
    @asyncio.coroutine
    async def reconnected_cb(self):
        self.logs.info("Reconectando a {url}".format(url=self.__nc.connected_url.netloc))
    
    @asyncio.coroutine
    async def error_cb(self, e):
        self.logs.error("[NATS] Ocurrio el siguiente Error: {}".format(e))

    @asyncio.coroutine
    async def closed_cb(self):
        self.logs.info("Se cerro la conexion al servidor de NATS")

    async def subscribe_handler(self, msg):
        # Convertir en un objeto la peticion recivida 
        DATA = self.__b64_to_json(msg.data)
        # Validar si es un Queue
        if self.__isQueue:
            # Asignar el ID para que le responda 
            DATA.update({"reply": msg.reply})

        # Pasar los datos
        await self._message(DATA)

    def __json_to_b64(self, json_in):
        """
            Metodo que pasa un objecto a el formato necesario
            para su comunicacion
        """
        JSON_SER = None
        try:
            JSON_SER = json.dumps(json_in)
        except:
            self.logs.error('Ocurrio un error al momento de serializar el JSON')

        return base64.b64encode(str.encode(JSON_SER))

    def __b64_to_json(self,encoded):
        """
            Metodo que conviernte un base64 a dict
        """
        decoded = base64.b64decode(encoded)
        return json.loads(decoded.decode('utf-8'))

    def _message(self, msg):
        """
            Metodo para el procesamiento de mensajes de
            Nats.
        """
        pass

    async def _send(self, reply, msj, idTransaction):
        """
            Metodo para el envio de datos a Nats

            @params reply Elemento al que se le responde
            @params msj Mensaje que enviara
            @params idTransaction Id de la transaccion
        """
        await self.__nc.publish(reply, self.__json_to_b64(msj))

    def isQueue(self):
        """
            Metodo para conocer si un queue worker
        """
        return self.__isQueue
