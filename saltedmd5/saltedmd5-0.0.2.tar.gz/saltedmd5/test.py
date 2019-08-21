## Salted Password Hashing by Nuttaphat Arunoprayoch
# Testing Area
from saltedmd5 import salting

class Member:
    ''' User Log-in Information '''
    def __init__(self, username, password, gram):
        self.username = username
        self.password = password
        self.res = salting(password, gram)
        self.salt_gram = gram

    def info(self):
        response = f'''
            Username: {self.username}
            Password: {self.password}
            Result: {self.res} '''
        return response


# Main Function
def main():
    user_1 = Member('test', 'test', 20)
    print(user_1.info())

    user_2 = Member('fernando', 'delgado', 8)
    print(user_2.info())


if __name__ == '__main__':
    main()
