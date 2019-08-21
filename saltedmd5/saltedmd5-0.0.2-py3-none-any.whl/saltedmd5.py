## Salted Password Hashing by Nuttaphat Arunoprayoch
# ref #1: https://crackstation.net/hashing-security.htm
# ref #2: https://stackoverflow.com/questions/49958006/python-3-create-md5-hash
import random
import string
import hashlib


# Salted Password Hashing Process
def salting(pwd, i):
    salt = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=i))
    m = hashlib.md5()
    salted_pwd = pwd + salt
    m.update(salted_pwd.encode('UTF-8'))

    data = {
        'password': pwd,
        'salted_password': m.hexdigest(),
        'salt': salt
    }

    return data


if __name__ == '__main__':
    print('Please use this module via \'import\'')
    exit()
