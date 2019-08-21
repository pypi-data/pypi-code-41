from ArduinoCodeCreator.arduino_data_types import *
from ArduinoCodeCreator.basic_types import Function, ArduinoClass, Array, Variable


class ArduinoBaseClass(ArduinoClass):
    # Digital I/O
    INPUT = Variable("INPUT", obscurable=False)
    OUTPUT = Variable("OUTPUT", obscurable=False)
    INPUT_PULLUP = Variable("INPUT_PULLUP", obscurable=False)
    EXTERNAL = Variable("EXTERNAL", obscurable=False)
    LOW = Variable("LOW", obscurable=False)
    HIGH = Variable("HIGH", obscurable=False)
    true = Variable("true", obscurable=False)
    false = Variable("false", obscurable=False)

    digitalRead = Function("digitalRead", [uint8_t], uint8_t)
    digitalWrite = Function("digitalWrite", [uint8_t, uint8_t])
    pinMode = Function("pinMode", [uint8_t, uint8_t])

    analogRead = Function("analogRead", [uint8_t], uint16_t)
    analogWrite = Function("analogWrite", [uint8_t, uint8_t])
    analogReference = Function("analogReference", [uint8_t])

    random = Function("random", arguments=[], return_type=uint16_t)
    randomSeed = Function(name="randomSeed", arguments=[uint32_t])
    memcpy = Function(
        name="memcpy", arguments=[uint8_t_pointer, uint8_t_pointer, uint8_t]
    )
    millis = Function(return_type=uint32_t, name="millis")
    max = Function(return_type=uint32_t, name="max", arguments=[uint32_t, uint32_t])
    min = Function(return_type=uint32_t, name="min", arguments=[uint32_t, uint32_t])
    delay = Function(name="delay", arguments=[uint32_t])
    sizeof = Function(name="sizeof", arguments=[uint32_t])


Arduino = ArduinoBaseClass()


class SerialClass(ArduinoClass):
    _tempvar_T = Variable("var", T)
    class_name = "Serial"
    begin = Function("begin", Variable("var", uint32_t))
    end = Function("end")
    read = Function("read", return_type=int16_t)
    peek = Function("peek", return_type=int16_t)
    flush = Function("flush")
    print = Function("print", _tempvar_T)
    print_format = Function("print", [_tempvar_T, Variable("format", uint8_t)])
    println = Function("println", _tempvar_T)
    println_format = Function("println", [_tempvar_T, Variable("format", uint8_t)])
    write = Function("write", Variable("var", uint16_t))
    write_buf = Function(
        "write", [Array("buffer", uint8_t), Variable("length", uint16_t)]
    )
    available = Function("available", return_type=int16_t)


Serial = SerialClass()


class EepromClass(ArduinoClass):
    class_name = "EEPROM"
    get = Function("get", [Variable("adress", uint16_t), Variable("target", uint32_t)])
    write = Function(
        "write", [Variable("adress", uint16_t), Variable("value", uint8_t)]
    )
    put = Function("put", [Variable("adress", uint16_t), Variable("source", uint32_t)])
    read = Function("read", [Variable("adress", uint16_t)], return_type=uint8_t)
    update = Function(
        "update", [Variable("adress", uint16_t), Variable("value", uint8_t)]
    )
    include = "<EEPROM.h>"


Eeprom = EepromClass()
