## Salted Password Hashing by Nuttaphat Arunoprayoch
# Testing Area
from saltedmd5 import Salting
import random

# Password and To-be-checked password
TEST_LISTS = {
    'test_1': 'test_1',
    'test_2': 45,
    'test_3': 'test3',
    'test_4': 'test_4',
    'test_5': 23+4j
}

# Expected Results
EXPECTED_RESULTS = [k==v for k, v in TEST_LISTS.items()]


def main():
    test_results = []

    for k, v in TEST_LISTS.items():
        user = Salting(k, random.randrange(10, 101))
        user.seasoning()
        user.show_info()
        # user.create_json('user')
        res = user.check_authentication(v)
        test_results.append(res)
    
    print('-' * 50)
    print('Expected Results: ', EXPECTED_RESULTS)
    print('Experimental Results: ', test_results)
    print('Satisfactory: ', test_results == EXPECTED_RESULTS)


if __name__ == '__main__':
    main()
