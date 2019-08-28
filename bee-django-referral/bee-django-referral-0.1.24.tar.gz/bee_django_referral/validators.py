#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'zhangyue'

import os
from django.core.exceptions import ValidationError


def jpg_validator(value):
    ext = os.path.splitext(value.name)[1]
    if not ext or not ext in [".jpg", ".jpeg"]:
        raise ValidationError(u'格式不正确，只能是jpg或jpeg格式图片')