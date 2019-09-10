import os
from pathlib import Path

def is_pic(file_name:Path):
    if not file_name.is_file():
        return False
    valid_suffix = ['.jpg', '.png', '.bmp']
    suffix = file_name.suffix
    return suffix.lower() in valid_suffix