# chat/consumers.py
from channels.generic.websocket import WebsocketConsumer
import json

import filter_dict
from arduino_controller.datalogger import DataLogger
from arduino_controller.serialport import SerialPortDataTarget
from django.apps import apps

from arduino_controller.serialreader.serialreader import SerialReaderDataTarget
from arduino_controller.board_api import ArduinoAPIWebsocketConsumer
from json_dict import JsonMultiEncoder
from plug_in_django.manage import logger

BOARDDATAWEBSOCKETRECEIVER = {}
PORTLISTENERWEBSOCKETRECEIVER = None
DATALOGGERWEBSOCKETRECEIVER = None


class WebsocketReceiver:
    def __init__(self, local_object):
        self.local_object = local_object
        self.ws_targets = []

    def receive(self, sdata):
        data = json.loads(sdata)
        type = data.get("type")
        if type == "cmd":
            self.cmd_message(data.get("data"))
        else:
            logger.error("Unknow message type: " + str(type))

    def cmd_message(self, data):
        if not isinstance(data, dict):
            logger.error("Invalid command structure: " + str(data))
            return
        cmd = data.get("cmd")
        try:
            if "data" not in data:
                data["data"] = {}
            data["data"]["data_target"] = self
            func = getattr(self.local_object, cmd)
            if func is None:
                logger.error("Unknown command: " + str(cmd))
            ans = filter_dict.call_method(target=func, kwargs=data["data"])
            if ans is not None:
                data = {"cmd": cmd, "data": ans}
                for target in self.ws_targets:
                    target.to_client(data, type="cmd")
        # except AttributeError as e:
        #     logger.error("Unknown command: "+ str(cmd))
        except Exception as e:
            logger.exception(e)


class BoardDataWebsocketReceiver(WebsocketReceiver, SerialPortDataTarget):
    def __init__(self, board_port):
        super().__init__(board_port)
        board_port.add_data_target(self)

    def board_update(self, board_data):
        data = {"cmd": "board_update", "board_data": board_data}
        for target in self.ws_targets:
            target.to_client(data, type="cmd")

    def set_board(self, port, board):
        data = {"cmd": "set_board", "port": port, "board": board}
        for target in self.ws_targets:
            target.to_client(data, type="cmd")

    def port_data_point(self, key, x, y, port, board):
        data = {
            "cmd": "port_data_point",
            "port": port,
            "key": key,
            "x": x,
            "y": y,
            "board": board,
        }
        for target in self.ws_targets:
            target.to_client(data, type="cmd")


class PortListenerWebsocketReceiver(WebsocketReceiver, SerialReaderDataTarget):
    def __init__(self, serial_reader):
        super().__init__(serial_reader)
        serial_reader.add_data_target(self)

    def set_ports(
        self, available_ports, ignored_ports, connected_ports, identified_ports
    ):
        data = {
            "cmd": "set_ports",
            "ports": dict(
                available_ports=available_ports,
                ignored_ports=ignored_ports,
                connected_ports=connected_ports,
                identified_ports=identified_ports,
            ),
        }
        for target in self.ws_targets:
            target.to_client(data, type="cmd")

    def port_identified(self, port):
        data = {"cmd": "port_identified", "port": port}
        for target in self.ws_targets:
            target.to_client(data, type="cmd")

    def port_opened(self, port, baud):
        data = {"cmd": "port_opened", "port": port, "baud": baud}
        for target in self.ws_targets:
            target.to_client(data, type="cmd")

    def port_closed(self, port):
        data = {"cmd": "port_closed", "port": port}
        for target in self.ws_targets:
            target.to_client(data, type="cmd")


class BoardDataConsumer(WebsocketConsumer):
    def connect(self):
        arg = self.scope["url_route"]["kwargs"].get("arg")
        socket_type = self.scope["url_route"]["kwargs"].get("socket_type")
        sr = apps.get_app_config("django_arduino_controller").serial_reader

        if sr is None:
            self.close(code=1234)
            return

        if socket_type == "board_data":
            global BOARDDATAWEBSOCKETRECEIVER
            if BOARDDATAWEBSOCKETRECEIVER.get(arg) is None:
                board_port = sr.get_identified_by_port(arg)
                if board_port is None:
                    self.close(code=5678)
                    return
                BOARDDATAWEBSOCKETRECEIVER[arg] = BoardDataWebsocketReceiver(board_port)
            self.receiver = BOARDDATAWEBSOCKETRECEIVER[arg]
        elif socket_type == "port_listener":
            global PORTLISTENERWEBSOCKETRECEIVER
            if PORTLISTENERWEBSOCKETRECEIVER is None:
                PORTLISTENERWEBSOCKETRECEIVER = PortListenerWebsocketReceiver(sr)
            self.receiver = PORTLISTENERWEBSOCKETRECEIVER
        else:
            self.close(code=91011)
            return

        self.receiver.ws_targets.append(self)
        self.accept()

    def disconnect(self, close_code):
        try:
            self.receiver.ws_targets.remove(self)
        except:
            pass

    def to_client(self, data=None, type=None):
        self.send(
            text_data=json.dumps({"data": data, "type": type}, cls=JsonMultiEncoder)
        )

    def receive(self, text_data=None, bytes_data=None):
        self.receiver.receive(text_data)


class DataLoggerSerialPortReceiver(SerialPortDataTarget):
    def __init__(self, dlsrwsr, board_port, datalogger):
        super().__init__()
        self.dlsrwsr = dlsrwsr
        self.datalogger = datalogger
        board_port.add_data_target(self)

    def port_data_point(self, key, x, y, port, board):
        added_key, added_x, added_y = self.datalogger.add_datapoint(
            key="{} ({})".format(key, board), x=x, y=y
        )
        if added_key is not None:
            data = {"cmd": "data_point", "key": added_key, "x": added_x, "y": added_y}
            for target in self.dlsrwsr.ws_targets:
                target.to_client(data, type="cmd")


class DataLoggerSerialReaderWebsocketReceiver(
    WebsocketReceiver, SerialReaderDataTarget
):
    def __init__(self, serial_reader):
        super().__init__(DataLogger())
        self.serial_reader = serial_reader
        self.board_receiver = {}
        serial_reader.add_data_target(self)

    def set_ports(
        self, available_ports, ignored_ports, connected_ports, identified_ports
    ):
        for port in [port_obj["port"] for port_obj in identified_ports]:
            if port not in self.board_receiver:
                try:
                    self.board_receiver[port] = DataLoggerSerialPortReceiver(
                        self,
                        self.serial_reader.get_identified_by_port(port),
                        self.local_object,
                    )
                except Exception as e:
                    logger.exception(e)


class DataLoggerConsumer(WebsocketConsumer):
    def connect(self):
        sr = apps.get_app_config("django_arduino_controller").serial_reader

        if sr is None:
            self.close(code=1234)
            return

        global DATALOGGERWEBSOCKETRECEIVER
        if DATALOGGERWEBSOCKETRECEIVER is None:
            DATALOGGERWEBSOCKETRECEIVER = DataLoggerSerialReaderWebsocketReceiver(sr)
        self.receiver = DATALOGGERWEBSOCKETRECEIVER

        self.receiver.ws_targets.append(self)
        self.accept()

    def disconnect(self, close_code):
        try:
            self.receiver.ws_targets.remove(self)
        except:
            pass

    def to_client(self, data=None, type=None):
        self.send(
            text_data=json.dumps({"data": data, "type": type}, cls=JsonMultiEncoder)
        )

    def receive(self, text_data=None, bytes_data=None):
        self.receiver.receive(text_data)


class APIConsumer(WebsocketConsumer, ArduinoAPIWebsocketConsumer):
    def connect(self):
        if (self.register_at_apis(self)):
            self.accept()
            self.start_broadcast()

    def disconnect(self, close_code):
        self.unregister_at_apis(self)

    def websocket_disconnect(self,message):
        self.disconnect(0)
        self.close()

    def receive(self, text_data=None, bytes_data=None):
        self.client_to_api(text_data)

    def to_client(self, data=None, type=None):
        self.send(
            text_data=json.dumps({"data": data, "type": type}, cls=JsonMultiEncoder)
        )
