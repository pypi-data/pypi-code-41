import os
import string
import random

import pandas as pd
from swissarmykit.utils.fileutils import FileUtils

class CanadaUtils:

    def __init__(self):
        self.current_path = FileUtils.get_path_of_file(__file__)
        pass

    def get_all_state(self):
        ''' https://www.quora.com/How-many-states-are-there-in-Canada
        3 territories: Northwest Territories, Nunavut, Yukon '''
        print('Warning: There is no state in Canada. Use get_all_provinces instead')

        return self.get_all_provinces()

    def get_all_provinces(self):
        return ['Alberta', 'British Columbia', 'Manitoba', 'New Brunswick', 'Newfoundland and Labrador', 'Nova Scotia', 'Ontario', 'Prince Edward Island', 'Quebec', 'Saskatchewan']

    def get_random_postcode_v1(self):

        ''' https://www.randomlists.com/canadian-postal-codes?qty=5000 Wrong format'''
        data = FileUtils.load_object_from_file(self.current_path + os.sep + 'random_postcode_ca.pickle')
        return data

    def get_random_postcode(self, default=''): # 1A1
        data = pd.read_csv(self.current_path + os.sep + 'ca_postal_codes.csv')

        AZ = [l for l in string.ascii_uppercase]
        _19 = [str(i) for i in range(10)]

        def get_rand_LDU():
            if default:
                return default
            return '%s%s%s' % (random.choice(_19), random.choice(AZ), random.choice(_19))

        lst = []
        for pc in data['Postal Code']:
            postcode = '%s %s' % (pc, get_rand_LDU())
            lst.append(postcode)
        random.shuffle(lst)
        return lst

    def get_cites_province(self):
        ''' https://www.britannica.com/topic/list-of-cities-and-towns-in-Canada-2038873 '''
        path = FileUtils.get_path_of_file(__file__)
        data = FileUtils.load_object_from_file(path + os.sep + 'cities_province_ca.pickle')
        lst = []
        for province, cities in data.items():
            for city in cities:
                item = '%s, %s' % (city, province)
                lst.append(item)
        return lst


if __name__ == '__main__':
    c = CanadaUtils()
    print(c.get_random_postcode())
    # print(c.get_cites_province())