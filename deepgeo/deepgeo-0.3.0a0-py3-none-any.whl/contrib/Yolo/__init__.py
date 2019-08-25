# __init__.py
# Copyright (C) 2019 Info Lab. (gnyontu39@gmail.com) and contributors
#
# 20190725 : pip install deepgeo opencv-python numpy

# Defalut Info
__deepgeo_category__ = "model"
__id__="Yolo"
__version__ = '0.0.190725.1'

try:
    from .Model import Model
    from .Dataset import Dataset
    from .Config  import Config
except ImportError as e:
    print(e," 추가할 수 없습니다.")
    exit(1)