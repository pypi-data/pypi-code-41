from epflldap.users.address import Address
import pandas as pd


class User:
    def __init__(self, data):
        self.data = data
        self.address = Address(data, type_data='person')
        # if self.address.is_address_complete() is False:
        #     unit = Unit(self.get_unit(), ldap_data.data['units'])
        #     self.address = Address(unit.unit_data, type_data='unit')

    def get_personal_status(self):
        """
        Retourne le statut personnel.
        """
        return self.data['attributes']['organizationalStatus'][0] \
            if 'organizationalStatus' in self.data['attributes'] else ''

    def get_first_name(self):
        """
        Retourne le prénom.
        """
        return self.data['attributes']['givenName'][0] \
            if 'givenName' in self.data['attributes'] else ''

    def get_last_name(self):
        """
        Retourne le nom de famille.
        """
        return self.data['attributes']['sn'][0]

    def get_sciper(self):
        """
        Retourne le sciper.
        """
        return self.data['attributes']['uniqueIdentifier'][0]

    def get_gender(self):
        """
        Retourne le genre.
        """
        return 'F' \
            if self.data['attributes']['personalTitle'][0] == 'Madame' else 'M'

    def get_phone_number(self):
        """
        Retourne le numéro de téléphone.
        """
        return self.data['attributes']['telephoneNumber'][0] \
            if 'telephoneNumber' in self.data['attributes'] else ''

    def get_email(self):
        """
        Retourne l'email.
        """
        return self.data['attributes']['mail'][0] \
            if 'mail' in self.data['attributes'] else ''

    def get_description(self):
        """
        Retourne l'intitulé de la fonction le plus détaillé.
        """
        if 'title' in self.data['attributes']:
            return self.data['attributes']['title'][0]

        if 'description' in self.data['attributes']:
            return self.data['attributes']['description'][0]

        if 'userClass' in self.data['attributes']:
            return self.data['attributes']['userClass'][0]

        return ''

    def get_civil(self):
        """
        Retourne l'état civil. Retourne la valeur indéfinie: '1595'.
        """
        return '1595'

    def get_unit(self):
        """
        Retourne l'unité
        """
        return self.data['attributes']['ou'][0]

    def get_unit_long(self):
        """
        Retourne l'unité
        """
        return self.data['attributes']['ou'][1] \
            if len(self.data['attributes']['ou']) > 1 else ''

    def get_school(self):
        """
        Retourne la faculté
        """
        pattern = self.data['dn']
        elems = pattern.split(',')[::-1]
        for elem in elems:
            if elem.startswith('ou='):
                return elem[3:].upper()
        return ''

    def get_institute(self):
        """
        Retourne l'institut: 2e "ou"
        """
        pattern = self.data['dn']
        elems = pattern.split(',')[::-1]
        elems = [elem[3:].upper() for elem in elems if elem.startswith('ou=')]
        return elems[1] if len(elems) > 1 else ''

    def get_groups(self):
        """
        Retourne la liste des groupes
        """
        return self.data['attributes']['memberOf'] \
            if 'memberOf' in self.data['attributes'] else []

    def get_accred_order(self):
        """
        Retourne le numéro d'ordre des accréditations
        """
        return self.data['attributes']['EPFLAccredOrder'][0] \
            if 'EPFLAccredOrder' in self.data['attributes'] else ''

    def get_BL(self):
        """
        Retourne le bl concerné
        """
        BLs = {'ENAC': 'CBC',
               'CDM': 'JD',
               'CDH': 'MP',
               'IC': 'JD',
               'ENT-E': 'JD'}
        return BLs[self.get_school()] if self.get_school() in BLs else 'JD'

    def get_info(self):
        """
        Retourne une série avec les principales informations sur un
        utilisateur.
        """
        values = [self.get_sciper(),
                  self.get_first_name(),
                  self.get_last_name(),
                  self.get_description(),
                  self.get_personal_status(),
                  self.get_school(),
                  self.get_institute(),
                  self.get_unit(),
                  self.get_email(),
                  self.get_phone_number(),
                  self.address.get_address_lines()[0],
                  self.address.get_address_lines()[1],
                  self.address.get_address_lines()[2]]

        index = ['Sciper',
                 'Prénom',
                 'Nom',
                 'Titre',
                 'Status',
                 'Faculté',
                 'Institut',
                 'Unité',
                 'Email',
                 'Téléphone',
                 'Adresse 1',
                 'Adresse 2',
                 'Adresse 3']

        return pd.Series(values, index=index)
