import pyAesCrypt
import os


# encryption/decryption buffer size - 64K

def check_if_user_exists():
    path_to_home = os.path.expanduser('~')
    if os.path.isfile(path_to_home + "/today/creds.json.aes"):
        return True
    else:
        return False


def create_log_file(self,key):

    pass


def write_and_encrypt(self):
    pass


def read_and_decrypt(self):
    pass


# bufferSize = 64 * 1024
# password = "foopassword"
# # encrypt
# pyAesCrypt.encryptFile("data.txt", "data.txt.aes", password, bufferSize)
# # decrypt
# pyAesCrypt.decryptFile("data.txt.aes", "dataout.txt", password, bufferSize)
