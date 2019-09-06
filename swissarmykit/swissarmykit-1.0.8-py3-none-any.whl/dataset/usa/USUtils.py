import os

import pyap
import us
import usaddress
from swissarmykit.data.Address import Address
from swissarmykit.lib.inspector import Inspector
from swissarmykit.utils.fileutils import FileUtils


class USUtils:
    '''
    State = {'abbr': 'AL',
             'ap_abbr': 'Ala.',
             'capital': 'Montgomery',
             'capital_tz': 'America/Chicago',
             'fips': '01',
             'is_contiguous': True,
             'is_continental': True,
             'is_obsolete': False,
             'is_territory': False,
             'name': 'Alabama',
             'name_metaphone': 'ALBM',
             'statehood_year': 1819,
             'time_zones': ['America/Chicago']}
    '''
    def __init__(self, ):
        pass

    def to_abr(self, state):
        state = us.states.lookup(state)
        return state.abbr if state else ''

    def get_all_states(self, abbr=False, key_value=False):
        if key_value:
            return {s.abbr: s.name for s in us.states.STATES}

        if abbr:
            return [s.abbr for s in us.states.STATES]
        return [s.name for s in us.states.STATES]

    def get_all_cities(self):
        path = FileUtils.get_path_of_file(__file__)
        data = FileUtils.load_object_from_file(path + os.sep + 'usa_cities.pickle')
        return  [city for cities in data.values() for city in cities]

    def lookup(self, state):
        return us.states.lookup(state)

    def parse_address(self, text, country='US'):
        addresses = pyap.parse(text, country=country)
        if addresses:
            return Address(addresses[0].as_dict(), text=text)
        addresses = usaddress.parse(text)
        if addresses:
            a = Address()
            a.set_data(addresses, address_text=text)
            return a

        return Address()


if __name__ == '__main__':
    u = USUtils()
    # print(u.to_abr())
    print(u.get_all_cities())

    # addr = '123 Main St. Suite 100 Chicago, IL'
    # addr = u.parse_address(addr)
    # print(addr)



