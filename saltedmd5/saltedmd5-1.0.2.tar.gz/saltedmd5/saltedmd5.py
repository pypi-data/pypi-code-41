## Salted Password Hashing by Nuttaphat Arunoprayoch
# ref #1: https://crackstation.net/hashing-security.htm
# ref #2: https://stackoverflow.com/questions/49958006/python-3-create-md5-hash

# Dependencies
import random
import string
import hashlib
import json
import pprint
pp = pprint.PrettyPrinter(indent=4)


# Salting Process and Ultilities (In-development)
class Salting:
    ''' Salted MD5 Hashing process and its ultilities '''
    def __init__(self, password, grams_of_salt):
        self.password = str(password)
        self.grams_of_salt = int(abs(grams_of_salt))
        self.is_seasoned = False

    def seasoning(self):
        ''' MD5 hasing process with Salt '''
        is_successful = False
        try:
            salt = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=self.grams_of_salt))
            m = hashlib.md5()
            salted_pwd = self.password + salt
            m.update(salted_pwd.encode('UTF-8'))
            self.data = {
                    'password': self.password,
                    'salted_password': m.hexdigest(),
                    'salt': salt
                }
            is_successful, self.is_seasoned = True, True

        except Exception as e:
            print('Whoops, something went terribly wrong with Seasoning :(')
            print(f'Error: {e}')

        return self.data if is_successful else None

    def show_info(self):
        ''' Display Information after seasoning '''
        if(self.is_seasoned):
            message = self.data
        else:
            message = 'Please use "seasoning" before showing information.'
        pp.pprint(message)

        return message

    def create_json(self, name_of_file):
        ''' Create JSON file from a given data after seasoning '''
        if(self.is_seasoned):
            try:
                with open(f'{name_of_file}.json', 'w') as f:
                    json.dump(self.data, f, ensure_ascii=False)
                print('JSON created!!')

            except Exception as e:
                print('Whoops, something went terribly wrong with Creating JSON :(')
                print(f'Error: {e}')

            return None

        else:
            return 'Please use "seasoning" before showing information.'

    def check_authentication(self, new_user_password):
        ''' Check the correctness between a given password and a salted one '''
        if(self.is_seasoned):
            m = hashlib.md5()
            salted_pwd = str(new_user_password) + self.data['salt']
            m.update(salted_pwd.encode('UTF-8'))
            new_user_password = m.hexdigest()

            # Display the result
            res = (new_user_password == self.data['salted_password'])
            if(res):
                print('Passwords matched!!')
            else:
                print('Passwords DID NOT match!!')

            return res

        else:
            return 'Please use "seasoning" before showing information.'


if __name__ == '__main__':
    print('Please use this module via \'import\'')
    exit()
