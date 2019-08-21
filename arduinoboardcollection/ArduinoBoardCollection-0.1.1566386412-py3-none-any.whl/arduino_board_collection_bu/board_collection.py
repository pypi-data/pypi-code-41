import os
from arduino_controller.parseboards import parse_path_for_boards

parse_path_for_boards(os.path.join(os.path.dirname(__file__), "boards"))
