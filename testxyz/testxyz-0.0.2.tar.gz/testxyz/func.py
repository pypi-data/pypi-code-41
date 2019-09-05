import requests


def test_func(num):
    a = requests.utils.default_headers()
    print(a)
    return num ** 2


test_func(3)
