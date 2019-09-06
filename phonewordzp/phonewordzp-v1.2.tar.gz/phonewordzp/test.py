from Phone import *
import sys
import unittest


class My_Test(unittest.TestCase):

    def test_decoding(self):
        number = '1-765-432-7890'
        phone_obj = Telephone_Book(number)
        self.assertEqual(phone_obj.decoding(), '17654327890')

    def test_decoding_10(self):
        number = '765-432-7890'
        phone_obj = Telephone_Book(number)
        self.assertEqual(phone_obj.decoding(), '7654327890')

    def test_decoding_false(self):
        number = '765-432'
        phone_obj = Telephone_Book(number)
        self.assertEqual(phone_obj.decoding(), False)

    def encode_numbers_11(self):
        number = '17654327890'
        phone_obj = Telephone_Book(number)
        self.assertEqual(phone_obj.decoding(), '1-765-432-7890')

    def encode_numbers_10(self):
        number = '7654327890'
        phone_obj = Telephone_Book(number)
        self.assertEqual(phone_obj.decoding(), '765-432-7890')

    def test_words_to_number(self):
        number = '1-CATS-AND-DOG'
        phone_obj = Telephone_Book(number)
        self.assertEqual(phone_obj.words_to_number(), '1-228-726-3364')

    def test_merge_list(self):
        l1 = ['abc', 'def']
        l2 = ['123', '456']
        number = '1-CATS-AND-DOG'
        l = ['a-b-c-1-2-3', 'a-b-c-4-5-6', 'd-e-f-1-2-3', 'd-e-f-4-5-6']
        phone_obj = Telephone_Book(number)
        self.assertEqual(phone_obj.merge_lists(l1, l2, []), l)

    def test_separate_0_1(self):
        number = '17263501'
        l = ['', '72635', '', '']
        phone_obj = Telephone_Book(number)

        self.assertEqual(phone_obj.separate_0_1(number), l)

    def test_get_word_1(self):
        number = '1-CATS-AND-DOG'
        phone_obj = Telephone_Book(number)
        substring = 'painter'
        self.assertEqual(phone_obj.get_word(substring), True)

    def test_get_word_2(self):
        number = '1-CATS-AND-DOG'
        phone_obj = Telephone_Book(number)
        substring = 'sdfbdnsjfk'
        self.assertEqual(phone_obj.get_word(substring), False)

    def test_substring(self):
        number = '1-CATS-AND-DOG'
        phone_obj = Telephone_Book(number)
        numbers = '7854'
        l = ['7', '78', '785', '7854', '8', '85', '854', '5', '54', '4']
        self.assertEqual(phone_obj.get_all_substring(numbers, len(numbers)), l)

    def test_all_worfications(self):
    	"""Test Valid sets of wordifications"""
    	number = '1-800-724-6837'
    	phone_obj = Telephone_Book(number)
    	if len(phone_obj.all_wordifications()) > 0:
    		x = True
    	else:
    		x = False
    	self.assertEqual(x, True)

    


if __name__ == '__main__':
    unittest.main()
