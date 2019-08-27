#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 Tongdun Inc. All Rights Reserved.
# @Time             : 2019/8/20 5:35 PM
# @Author           : ding
# @File             : image2jsons.py
# @description      :
import json
import argparse
import os

from tdserver import ImageServer

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--image', help=u"输入图像路径")

    args = parser.parse_args()

    name = os.path.basename(args.image)
    with open(name + '.json', 'w', encoding='utf-8') as wf:
        with open(args.image, 'rb') as f:
            idict = ImageServer.encode_warpimg(f.read())

            json.dump(idict, wf)
