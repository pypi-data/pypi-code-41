import os
import time

import numpy as np


def generate_pseudorandom_firmware():
    aa = np.uint64(int(str(time.time()).replace(".", ""))).tobytes()
    ba = bytearray(
        reversed(np.uint64(int(str(time.time()).replace(".", ""))).tobytes())
    )
    r = np.random.bytes(8)
    for i in range(len(ba)):
        if ba[i] == 0:
            ba[i] = r[i]
        else:
            break
    return np.frombuffer(ba, dtype=np.uint64)[0]


def create_board(path, name, superboard="ArduinoBasicBoard"):
    camelcase = "".join(x for x in name.title() if not x.isspace())
    snakename = name.lower().replace(" ", "_")
    os.makedirs(os.path.join(path, snakename), exist_ok=True)
    firmware = generate_pseudorandom_firmware()
    if os.path.exists(os.path.join(path, snakename, "board.py")):
        raise ValueError(
            name + "already exists as board: " + str(os.path.join(path, snakename))
        )

    with open(os.path.join(path, snakename, "board.py"), "w+") as f:
        code = ""
        code += "from ArduinoCodeCreator.arduino import *\n"
        code += "from ArduinoCodeCreator.arduino_data_types import *\n"
        code += "from ArduinoCodeCreator.basic_types import *\n"
        code += "from ArduinoCodeCreator.statements import *\n"
        code += "from arduino_controller.arduino_variable import arduio_variable\n"
        code += "from arduino_controller.basicboard.board import ArduinoBoardModule, BasicBoardModule, ArduinoBoard\n"
        code += "from arduino_controller.python_variable import python_variable\n"
        code += "\n"
        code += "\n"
        code += "class {}Module(ArduinoBoardModule):\n".format(camelcase)
        code += "\t# depencies\n"  #
        code += "\tbasic_board_module = BasicBoardModule\n"
        code += "\n"
        code += "\t# python_variables\n"
        code += "\n"
        code += "\t# arduino_variables\n"
        code += "\n"
        code += "\tdef instance_arduino_code(self, ad):\n"
        code += "\t\tad.loop.add_call()\n"
        code += "\t\tad.setup.add_call()\n"
        code += "\t\tself.basic_board_module.dataloop.add_call()\n"
        code += "\n"
        code += "\n"
        code += "class {}Board(ArduinoBoard):\n".format(camelcase)
        code += "\tFIRMWARE = {}\n".format(firmware)
        code += "\tmodules = [{}Module]\n".format(camelcase)
        code += "\n"
        code += "\n"
        code += "if __name__ == '__main__':\n"
        code += "\tins = {}Board()\n".format(camelcase)
        code += "\tins.create_ino()"
        f.write(code.replace("\t", "    "))


if __name__ == "__main__":
    create_board(
        path=os.path.join(os.path.dirname(__file__), "boards", "test"),
        name="autocreated " + str(int(time.time())),
    )
