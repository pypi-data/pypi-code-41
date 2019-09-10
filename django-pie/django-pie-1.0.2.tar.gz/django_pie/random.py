# coding: utf-8
import uuid
import random


def uuid_str(dash=False, method='uuid4'):
    s = getattr(uuid, method)
    return str(s()) if dash else s().hex


def random_str(length=16, upper=False, lower=False, alpha=True, number=True, special=False):
    if not alpha and not number and not special:
        raise ValueError('alpha, number and special can not be False together.')
    sample = ''
    if alpha:
        sample += 'abcdefghijklmnopqrstuvwxyz' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if number:
        sample += '0123456789'
    if special:
        sample += '!@#$%^&*,.;'
    s = ''.join([random.choice(sample) for _ in range(length)])
    if upper:
        return s.upper()
    elif lower:
        return s.lower()
    return s
