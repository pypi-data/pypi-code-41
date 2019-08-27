import re


class Address:
    def __init__(self, data, type_data='person'):
        self.data = data
        self.type_data = type_data

    def is_address_complete(self):
        """
        Retourne True si l'attribut "postalAddress" n'est pas satisfaisant.
        """
        if 'postalAddress' in self.data['attributes']:
            if len(self.data['attributes']['postalAddress'][0]) > 0:
                return True
        else:
            return False

    def is_service_address(self):
        """
        Retourne True si l'adressse est une adresse de service.
        """
        return False if self.type_data == 'person' else True

    def get_country_code(self):
        """
        Retourne le code correspondant à la Suisse: '8100'.
        """
        return '8100'

    def get_address_lines(self):
        """
        Retourne les adresses, sauf la localité et le code postal jusqu'en
        trois lignes.
        """
        if 'postalAddress' in self.data['attributes']:
            address_lines = [line.strip() for line in
                             self.data['attributes']['postalAddress'][0]
                             .split('$')
                             if not(re.match(r'^\s*[A-Z]{2}\-\d{4,5}', line))]

            if len(address_lines) > 3:
                address_lines = address_lines[:3]

            for i in range(3):
                if i >= len(address_lines):
                    address_lines.append('')
            return address_lines

        return ['', '', '']

    def get_zip_code(self):
        """
        Retourne le code postal.
        """
        if 'postalCode' in self.data['attributes']:
            postal_code = self.data['attributes']['postalCode'][0]
            test_re = re.search(r'[A-Z]{2}\-(\d{4,5})', postal_code)
            if test_re is not None:
                return test_re.group(1)

        if 'postalAddress' in self.data['attributes']:
            postal_code = [line.strip() for line in
                           self.data['attributes']['postalAddress'][0]
                           .split('$')
                           if re.match(r'^\s*[A-Z]{2}\-\d{4,5}', line)][0]
            test_re = re.search(r'[A-Z]{2}\-(\d{4,5})', postal_code)
            if test_re is not None:
                return test_re.group(1)

        return ''

    def get_posn_postal(self):
        """
        Retourne le code postal avec 2 zéros après.
        """
        return '' if self.get_zip_code() == '' else self.get_zip_code() + '00'

    def get_city(self):
        """
        Retourne la ville.
        """
        if 'postalAddress' in self.data['attributes']:
            city = [line.strip() for line in
                    self.data['attributes']['postalAddress'][0].split('$')
                    if re.match(r'^\s*[A-Z]{2}\-\d{4,5}', line)][0]
            test_re = re.search(r'[A-Z]{2}\-\d{4,5}\s(\D*)', city)
            if test_re is not None:
                return test_re.group(1).strip()
        return ''
