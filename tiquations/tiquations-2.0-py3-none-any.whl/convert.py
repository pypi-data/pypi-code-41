import math
import os

def Kelvin_C(Celsius):
    """Usage: Convert to Kelvin from Celsius
    Kelvin_C(Celsius)"""
    return Celsius+273.15

def Kelvin_F(Fahrenheit):
    """Usage: Convert to Kelvin from Fahrenheit
    Kelvin_F(Fahrenheit)"""
    return  (Fahrenheit-32) * 5/9 + 273.15

def Celsius_K(Kelvin):
    """Usage: Convert to Celsius from Kelvin
    Celsius_K(Kelvin)"""
    return Kelvin-273.15

def Celsius_F(Fahrenheit):
    """Usage: Convert to Celsius from Fahrenheit
    Celsius_F(Fahrenheit)"""
    return  (Fahrenheit-32)*5/9

def Fahrenheit_C(Celsius):
    """Usage: Convert to Fahrenheit from Celsius
    Fahrenheit_C(Celsius)"""
    return (Celsius* 9/5)+32

def Fahrenheit_K(Kelvin):
    """Usage: Convert to Fahrenheit from Kelvin
    Fahrenheit_K(Kelvin)"""
    return (Kelvin-273.15)*9/5 + 32

def bits(bytes=None, kilobytes=None,megabytes=None,gigabytes=None,terabytes=None,petabytes=None):
    """Usage: Convert to bits. Example: bits(megabytes=23)"""
    if bytes is not None:
        return bytes*8
    elif kilobytes is not None:
        return kilobytes*8000
    elif megabytes is not None:
        return megabytes*8e+6
    elif gigabytes is not None:
        return gigabytes*8e+9
    elif terabytes is not None:
        return terabytes*8e+12
    elif petabytes is not None:
        return petabytes*8e+15
    else:
        raise Exception("You must specify one value. Example: bytes, kilobytes, megabytes, gigabytes, terabytes, petabytes")


def bytes(bits=None, kilobytes=None,megabytes=None,gigabytes=None,terabytes=None,petabytes=None):
    """Usage: Convert to bytes. Example: bytes(gigabytes=2)"""
    if bits is not None:
        return bits/8
    elif kilobytes is not None:
        return kilobytes*1000
    elif megabytes is not None:
        return megabytes*1e+6
    elif gigabytes is not None:
        return gigabytes*1e+9
    elif terabytes is not None:
        return terabytes*1e+12
    elif petabytes is not None:
        return petabytes*1e+15
    else:
        raise Exception("You must specify one value. Example: bits, kilobytes, megabytes, gigabytes, terabytes, petabytes")

def kilobytes(bits=None, bytes=None,megabytes=None,gigabytes=None,terabytes=None,petabytes=None):
    """Usage: Convert to kilobytes. Example: kilobytes(bytes=86237)"""
    if bits is not None:
        return bits/8000
    elif bytes is not None:
        return bytes/1000
    elif megabytes is not None:
        return megabytes*1000
    elif gigabytes is not None:
        return gigabytes*1e+6
    elif terabytes is not None:
        return terabytes*1e+9
    elif petabytes is not None:
        return petabytes*1e+12
    else:
        raise Exception("You must specify one value. Example: bits, bytes, megabytes, gigabytes, terabytes, petabytes")

def megabytes(bits=None, bytes=None,kilobytes=None,gigabytes=None,terabytes=None,petabytes=None):
    """Usage: Convert to megabytes. Example: megabytes(bits=42561261)"""
    if bits is not None:
        return bits/8e+6
    elif bytes is not None:
        return bytes/1e+6
    elif kilobytes is not None:
        return kilobytes/1000
    elif gigabytes is not None:
        return gigabytes*1000
    elif terabytes is not None:
        return terabytes*1e+6
    elif petabytes is not None:
        return petabytes*1e+9
    else:
        raise Exception("You must specify one value. Example: bits, bytes, kilobytes, gigabytes, terabytes, petabytes")

def gigabytes(bits=None, bytes=None,kilobytes=None,megabytes=None,terabytes=None,petabytes=None):
    """Usage: Convert to gigabytes. Example: gigabytes(terabytes=2)"""
    if bits is not None:
        return bits/8e+9
    elif bytes is not None:
        return bytes/1e+9
    elif kilobytes is not None:
        return kilobytes/1e+6
    elif megabytes is not None:
        return megabytes/1000
    elif terabytes is not None:
        return terabytes*1000
    elif petabytes is not None:
        return petabytes*1e+6
    else:
        raise Exception("You must specify one value. Example: bits, bytes, kilobytes, megabytes, terabytes, petabytes")

def terabytes(bits=None, bytes=None,kilobytes=None,megabytes=None,gigabytes=None,petabytes=None):
    """Usage: Convert to terabytes. Example: terabytes(gigabytes=512)"""
    if bits is not None:
        return bits/8e+12
    elif bytes is not None:
        return bytes/1e+12
    elif kilobytes is not None:
        return kilobytes/1e+9
    elif megabytes is not None:
        return megabytes/1e+6
    elif gigabytes is not None:
        return gigabytes/1000
    elif petabytes is not None:
        return petabytes*1000
    else:
        raise Exception("You must specify one value. Example: bits, bytes, kilobytes, megabytes, gigabytes, petabytes")

def petabytes(bits=None, bytes=None,kilobytes=None,megabytes=None,gigabytes=None,terabytes=None):
    """Usage: Convert to petabytes. Example: petabytes(gigabytes=123456)"""
    if bits is not None:
        return bits/ 8e+15
    elif bytes is not None:
        return bytes/1e+15
    elif kilobytes is not None:
        return kilobytes/1e+12
    elif megabytes is not None:
        return megabytes/1e+9
    elif gigabytes is not None:
        return gigabytes/1e+6
    elif petabytes is not None:
        return petabytes/1000
    else:
        raise Exception("You must specify one value. Example: bits, bytes, kilobytes, megabytes, gigabytes, terabytes")

def km_miles(kilometers):
    """Usage: Convert kilometers to miles"""
    return kilometers/1.609

def miles_km(miles):
    """Usage: Convert miles to kilometers"""
    return kilometers*1.609
