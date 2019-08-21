from ArduinoCodeCreator import basic_types as at
from ArduinoCodeCreator.arduino import Arduino
from ArduinoCodeCreator.arduino_data_types import *
from ArduinoCodeCreator.basic_types import Variable
from ArduinoCodeCreator.statements import for_
from arduino_controller.basicboard.board import (
    ArduinoBoardModule,
    BasicBoardModule,
    ArduinoBoard,
)
from arduino_controller.arduino_variable import arduio_variable

class HX711(at.ArduinoClass):
    class_name = "HX711"
    gains = at.ArduinoEnum(
        "MotorInterfaceType",
        {
            128: ("128", "channel A, gain factor 128"),
            64: ("64", "channel A, gain factor 64"),
            32: ("32", "channel B, gain factor 32"),
        },
    )

    begin = at.Function("begin", [uint8_t, uint8_t, uint8_t])
    is_ready = at.Function("is_ready", return_type=bool_)
    wait_ready = at.Function("wait_ready", uint32_t)
    wait_ready_retry = at.Function(
        "wait_ready_retry", [uint16_t, uint32_t], return_type=bool_
    )
    wait_ready_timeout = at.Function(
        "wait_ready_timeout", [uint16_t, uint32_t], return_type=bool_
    )
    set_gain = at.Function("set_gain", uint8_t)
    read = at.Function("read", return_type=long_)
    read_average = at.Function("read_average", uint8_t, return_type=long_)
    get_value = at.Function("get_value", uint8_t, return_type=double_)
    get_units = at.Function("get_units", uint8_t, return_type=float_)
    tare = at.Function("tare", uint8_t)
    set_scale = at.Function("set_scale", float_)
    get_scale = at.Function("get_scale", return_type=float_)
    set_offset = at.Function("set_offset", long_)
    get_offset = at.Function("get_offset", return_type=long_)
    power_down = at.Function("power_down")
    power_up = at.Function("power_up")

    include = "<HX711.h>"

#https://github.com/EdwinCroissantArduinoLibraries/SimpleHX711
#([^\s]*) ([^\s]*)\((.*)\); with $2 = at.Function("$2",$3,return_type=$1)
# ,, with ,
#,return_type=void with


class HX711Module(ArduinoBoardModule):
    # depencies
    basic_board_module = BasicBoardModule
    #sets minimum datarate
    basic_board_module.data_rate.minimum = max(basic_board_module.data_rate.minimum,180)

    # arduino_variables
    hx711 = HX711()
    hx711_scale = hx711("hx711_scale")
    doutPin = arduio_variable(
        name="doutPin", arduino_data_type=uint8_t, eeprom=True, default=2
    )
    sckPin = arduio_variable(
        name="sckPin", arduino_data_type=uint8_t, eeprom=True, default=3
    )
    gain = arduio_variable(
        name="gain",
        arduino_data_type=uint8_t,
        eeprom=True,
        allowed_values=HX711.gains.possibilities,
    )
    scale = arduio_variable(
        name="scale",
        arduino_data_type=float_,
        eeprom=True,
        html_attributes={"step": 0.1},
    )
    offset = arduio_variable(name="offset", arduino_data_type=long_, eeprom=True)
    nread = arduio_variable(name="nread", arduino_data_type=uint8_t, eeprom=True)
    value = arduio_variable(
        name="value",
        arduino_data_type=float_,
        arduino_setter=None,
        is_data_point=True,
        changeable=False,
        save=False,
    )
    reinitalize_hx711 = at.Function("reinitalize_hx711")

    def instance_arduino_code(self, ad):

        self.reinitalize_hx711.add_call(
            self.hx711_scale.power_down(),
            self.hx711_scale.begin(self.doutPin, self.sckPin, self.gain),
            self.hx711_scale.wait_ready_timeout(1000, 0),
            self.hx711_scale.set_scale(self.scale),
            self.hx711_scale.set_offset(self.offset),
        )

        self.doutPin.arduino_setter.add_call(self.reinitalize_hx711())
        self.sckPin.arduino_setter.add_call(self.reinitalize_hx711())
        self.gain.arduino_setter.add_call(self.hx711_scale.set_gain(self.gain))

        self.scale.arduino_setter.add_call(self.hx711_scale.set_scale(self.scale))
        self.scale.arduino_getter.prepend_call(
            self.scale.set(self.hx711_scale.get_scale())
        )

        self.offset.arduino_setter.add_call(self.hx711_scale.set_offset(self.offset))
        self.offset.arduino_getter.prepend_call(
            self.offset.set(self.hx711_scale.get_offset())
        )

        ad.setup.add_call(self.reinitalize_hx711())
        self.basic_board_module.dataloop.prepend_call(
            self.value.set(self.hx711_scale.get_units(self.nread))
        )


class HX711Board(ArduinoBoard):
    FIRMWARE = 1712005307122661283
    modules = [HX711Module]


if __name__ == "__main__":
    ins = HX711Board()
    print("AA")
    ins.create_ino()
