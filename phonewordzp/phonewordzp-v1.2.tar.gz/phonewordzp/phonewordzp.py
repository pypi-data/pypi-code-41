import sys
import re
import random
#English Dictionary Package
import enchant
import time
from itertools import permutations

#Global Variables
Phone_Directory = {
		 '2': ['A', 'B', 'C'],
                 '3': ['D', 'E', 'F'],
                 '4': ['G', 'G', 'I'],
                 '5': ['J', 'K', 'L'],
                 '6': ['M', 'N', 'O'],
                 '7': ['P', 'Q', 'R', 'S'],
                 '8': ['T', 'U', 'V'],
                 '9': ['W', 'X', 'Y', 'Z']}

Check_Word = enchant.Dict("en_US")

#Telephone class
class Telephone_Book:
    def __init__(self, string):
        """An inheritage Class for getting the phone number and reusable structure"""
        #a Time to check how long for program to run
        self.start_time = time.time()
        self.string = string
        # A dictionary to store 0 and 1 from the original phone number with indexes
        self.indexs_0_1 = None
        # A hash table to store numbers and generated list of words '2'->['2', 'A', 'B', 'C'], '228'->['CAT', '2AT'...]
        self.hash_table = {}
        #all the words generation from numbers
        self.all_combinations = []
       


    def number_to_words(self):
        """Randomly output a solution from all_wordifications, A solution combined Words and Numbers"""
        self.all_wordifications()
        x = random.randrange((len(self.all_combinations)-1))
        elapsed_time = time.time() - self.start_time
        print('\nRequest Time: {}\n'.format(elapsed_time))
        return self.all_combinations[x]





    def words_to_number(self):
        """Convert words to numbers and format it"""
        # decode the string by removing all unnecessary chars
        clean_words = self.decoding()
        # if the string input is not a telephone, exit program
        if not clean_words:
            sys.exit("Wrong Input len or char, retry")

        string_list = [s for s in clean_words]
        for index in range(len(string_list)):
            for number, letter in Phone_Directory.items():
                if string_list[index] in letter:
                    string_list[index] = number
        elapsed_time = time.time() - self.start_time
        print('\nRequest Time: {}\n'.format(elapsed_time))
        return self.encoding_numbers(''.join(string_list))


    

    def all_wordifications(self):
        """ In order to get all wordifications, following steps are met:
            1) remove '-(){}' chars from phone number, reject number is len(number) != 10/11
            2) divide the string into different parts by 0 and 1
            3) for each part, get all the combinations of English word and numbers, for instance '228' = [['CAT'], ['CA', '8']...]
            4) assign the parts' solution:
                part = '228', solution l append ('2', '28'), ('228'), ('22', '8'), note ('2', '28') and ('228')'s solution equals len(part).
            5) store part '228' as key, and solution l as value in hashtable
            6) Assemble all the parts solutions to a list of solutions with added 0 and 1
        """
        # decode the string by removing all unnecessary chars
        clean_words = self.decoding()
        # if the string input is not a telephone, exit program
        if not clean_words:
            sys.exit("Wrong Input len or char, retry")
        #get divider by 0 and 1
        divider = self.separate_0_1(clean_words)
        #generate word solutions from parts and stored in hash table
        self.generate_hash_table(divider)
        #generate the full solutions from hash table
        self.generate_solutions()
        elapsed_time = time.time() - self.start_time
        print('\nRequest Time: {}\n'.format(elapsed_time))
        return self.all_combinations

        
        

    def encoding_words(self, raw_string):
        """Encode words by regular expression"""
        clean_words = re.sub('[\W_]+', '', raw_string)
        return raw_string[0:1]+'-'+raw_string[1:] if len(clean_words) == 11 else raw_string
       
       

    def add_0_1(self, l):
        """add the 0 and 1s back to numbers given all the possible solutions"""
        for s in l:
            index = 0
            #split into list
            list_s = [char for char in s]
            for i in range(len(list_s)):
                if index in self.indexs_0_1:
                    list_s.insert(i, self.indexs_0_1[index])
                if list_s[i] != '-':
                    index += 1
            answer = self.encoding_words(''.join(list_s))
            self.all_combinations.append(answer)

     
    def generate_solutions(self):
        """Generate all the solutions from parts"""
        stack = []
        for key, value in self.hash_table.items():
            stack.append(value)
        l = []
        l1 = stack.pop(0)
        while stack:
            l2 = stack.pop(0)
            l = self.merge_lists(l1, l2, l)
        self.add_0_1(l)
        

    def merge_lists(self, l1, l2, l):
        """Given 2 list, generate the assemble string from l1 and l2"""
        for i1 in l1:
            s1 = '-'.join(i1)
            for i2 in l2:
                s2 = '-'.join(i2)
                l.append(s1+'-'+s2)
        return l

    
    def generate_hash_table(self, divider):
        """By removing 0 and 1 from cleaned phone number, append to hash table is part is valid
            For instance '' is a divider generate from 0,1s, ignore
                         '78342' is a valid part that can iterate all the words and numbers"""
        for div in divider:
            #stop if the subsequence are too large
            if len(div) > 8:
                sys.exit("Phone number len(n) > 8 are too large for dictionary to generate, retry.")
            if div and len(div) > 1:
                self.hash_table[div] = self.get_all_word(div)
            elif len(div) == 1:
                self.hash_table[div] = Phone_Directory[div]
                #add original number
                self.hash_table[div].append(div)
           

    def get_all_word(self, numbers):
        """For one part, generate all the combinations of words and letters which is a valid solution. 
            numbers = '228', s = ['CAT', 'C28', 'CA8'....]
                                                            """
        numbers_combinations = self.get_all_substring(numbers, len(numbers))
        word_table = self.generate_words(numbers_combinations, {})
        return self.generate_combinations(word_table, numbers)
        


    def get_all_substring(self, numbers, n):
        """Given numbers, return all sub-numbers, '228'-> '228', '22', '28', '2', '8'"""
        l = []
        for i in range(n):
            for len in range(i+1, n+1):
                l.append(numbers[i:len])
        return l

    def generate_words(self, l, table):
        """for all sub-numbers, find its English Word"""
        for i in l:
            #add number as well, since CAT-S and CAT-7 are different
            combinations = [i]
            self.backtrack("", i, combinations)
            table[i] = combinations
        return table

    #most time consuming N^3 to N^4
    def backtrack(self, combination, next_digits, output):
        """Given a number, find all possible English combination from Phone Directory, and append it if the combination is an English word"""
        if len(next_digits) == 0:
            if self.get_word(combination):
                #only append number combinations if the combinations is found in English Dictionary
                output.append(combination)
        else:
            for letter in Phone_Directory[next_digits[0]]:
                self.backtrack(combination + letter, next_digits[1:], output)

    def generate_combinations(self, word_table, numbers):
        """Getting all substrings' word solution, append the solution to part, if substring1 + substring2 = numbers
            numbers = '793', concate '7'+'93''s solution, '793''s solution, '79'+'3''s solutions """
        keys = [key for key, value in word_table.items()]
        seq = permutations(keys, 2)
        l = []
        #create paris of all substring ('7', '79'), ('7', '793')
        for p in list(seq):
            if p[0]+p[1] == numbers:
                #only if the two pairs are match numbers
                self.merge_keys(word_table[p[0]], word_table[p[1]], word_table, l)
        return l

    def merge_keys(self, l1, l2, word_table, l):
        """Concate subsolutions l1 = '7''s solution, l2 = '93's solution, 
            l = '793's solution """
        for i in l1:
            for j in l2:
                l.append([i, j])
        return l


    def separate_0_1(self, clean_words):
        """Separate String by 0 and 1 into different parts, store 0s and 1s location in self.indexs_0_1"""
        self.indexs_0_1 = {index:number for index, number in enumerate(clean_words) if number == '0' or number == '1'}
        regex = re.compile('[0-1]')
        return regex.split(clean_words)

    def get_word(self, sub_string):
        """Using Enchant to check if given a substring, if the substring is a Enlish Word"""
        return Check_Word.check(sub_string)


    
    def decoding(self):
        """For all the income numbers(words/letter), remove all other chars, and check if it is a valid phone number"""
        x = re.sub('[\W_]+', '', self.string)
        return x if len(x) == 10 or len(x) == 11 else False


    def encoding_numbers(self, raw_string):
        """Format numbers only phone number by phone number's length"""
        # 876-678-1000
        if len(raw_string) == 10:
            return raw_string[0:3] + '-' + raw_string[3:6] + '-' + raw_string[6:]
        # 1-876-678-1000
        else:
            return raw_string[0] + '-' + raw_string[1:4] + '-' + raw_string[4:7] + '-' + raw_string[7:]


