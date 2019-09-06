
'''
{'full_address': '2 Rockwood Street in Rochester, NY 14610', 'full_street': '2 Rockwood Street', 'street_number': '2', 'street_name': 'Rockwood', 'street_type': 'Street', 'route_id': None, 'post_direction': None, 'floor': None, 'building_id': None, 'occupancy': None, 'city': 'in Rochester', 'region1': 'NY', 'postal_code': '14610', 'country_id': 'US'}
'''

class Address:
    usaddress_label = {
        'AddressNumberPrefix' : '',
        'AddressNumber' : 'street_number',
        'AddressNumberSuffix' : '',
        'StreetNamePreModifier' : '',
        'StreetNamePreDirectional' : '',
        'StreetNamePreType' : '',
        'StreetName' : 'street_name',
        'StreetNamePostType' : '',
        'StreetNamePostDirectional' : '',
        'SubaddressType' : '',
        'SubaddressIdentifier' : '',
        'BuildingName' : 'building_id',
        'OccupancyType' : '',
        'OccupancyIdentifier' : 'occupancy',
        'CornerOf' : '',
        'LandmarkName' : '',
        'PlaceName' : 'city',
        'StateName' : 'region1',
        'ZipCode' : 'postal_code',
        'USPSBoxType' : '',
        'USPSBoxID' : '',
        'USPSBoxGroupType' : '',
        'USPSBoxGroupID' : '',
        'IntersectionSeparator' : '',
        'Recipient' : '',
        'NotAddress' : '',
    }

    def __init__(self, data=None, text=''):
        self.full_address = ''
        self.full_street = ''
        self.street_number = ''
        self.street_name = ''
        self.street_type = ''
        self.route_id = ''
        self.post_direction = ''
        self.floor = ''
        self.building_id = ''
        self.occupancy = ''
        self.city = ''
        self.region1 = ''
        self.postal_code = ''
        self.country_id = ''

        self.data = data
        self.address_text = text

        if data:
            self.full_address = data.get('full_address', '')
            self.full_street = data.get('full_street', '')
            self.street_number = data.get('street_number', '')
            self.street_name = data.get('street_name', '')
            self.street_type = data.get('street_type', '')
            self.route_id = data.get('route_id', '')
            self.post_direction = data.get('post_direction', '')
            self.floor = data.get('floor', '')
            self.building_id = data.get('building_id', '')
            self.occupancy = data.get('occupancy', '')
            self.city = data.get('city', '')
            self.region1 = data.get('region1', '')
            self.postal_code = data.get('postal_code', '')
            self.country_id = data.get('country_id', '')

    def set_data(self, addresses, address_text='', usaddress_lib=True):
        if usaddress_lib:
            for item in addresses:
                value, name = item
                mapped = Address.usaddress_label.get(name)
                if mapped:
                    setattr(self, mapped, value)
            if self.get_city() and address_text:
                self.address_text = address_text
                self.full_street = address_text.rsplit(self.get_city(), 1)[0]

    def get_data(self):
        return self.data

    def as_dict(self):
        return self.data

    def get_zip_code(self):
        return self.postal_code

    def get_city(self):
        return self.city

    def get_state(self):
        return self.region1

    def get_street_address(self):
        return self.full_street

    def get_full_address(self):
        return self.full_address

    def get_city_state_zip(self):
        return self.get_city(), self.get_state(), self.get_zip_code()

    def __str__(self):
        return '''      full_address = %s
    full_street = %s
    street_number = %s
    street_name = %s
    street_type = %s
    route_id = %s
    post_direction = %s
    floor = %s
    building_id = %s
    occupancy = %s
    city = %s
    region1 = %s
    postal_code = %s
    country_id = %s
        ''' % (self.full_address,
               self.full_street,
               self.street_number,
               self.street_name,
               self.street_type,
               self.route_id,
               self.post_direction,
               self.floor,
               self.building_id,
               self.occupancy,
               self.city,
               self.region1,
               self.postal_code,
               self.country_id)
