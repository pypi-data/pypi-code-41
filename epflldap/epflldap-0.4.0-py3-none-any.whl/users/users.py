import pandas as pd


class Users:
    """
    Classe comprenant une liste d'utilisateurs
    """
    @staticmethod
    def _to_lower_case(list_txt):
        """
        retourne une liste en minuscules uniquement.
        """
        return [txt.lower() for txt in list_txt]

    def __init__(self, users):
        """
        Constructeur de la liste des utilisateurs.
        """
        self.data = users

    def __iter__(self):
        """
        Itérateur qui permet d'itérer sur tous utilisateurs.
        """
        for user in self.data:
            yield user

    def __getitem__(self, key):
        """
        Retourne un utilisateur en fonction d'un indice.
        """
        return self.data[key]

    def filter_by_group(self, group):
        """
        Filtre les utilisateurs en fonction d'un groupe. Retourne un nouvel
        objet Users.
        """
        return Users([user for user in self
                      if group.lower()
                      in self._to_lower_case(user.get_groups())])

    def filter_by_status(self, status):
        """
        Filtre les utilisateurs en fonction du statut. Retourne un nouvel objet
        Users.
        """
        return Users([user for user in self
                      if user.get_personal_status().lower()
                      in self._to_lower_case(status)])

    def filter_by_unit(self, unit):
        """
        Filtre en fonction du nom de l'unité. Retourne un nouvel objet Users.
        """
        return Users([user for user in self if unit == user.get_unit()])

    def filter_by_school(self, school):
        """
        Filtre en fonction du nom la faculté.
        """
        return Users([user for user in self
                      if school.lower() == user.get_school().lower()])

    def filter_by_first_accred(self):
        """
        Filtre les utilisateurs en ne renvoyant que leur première accréditation
        ou celle de rang le plus élevé. Cela permet de supprimer les doublons.
        On perd l'information d'une double affiliation toutefois.
        """
        sciper = {}
        for i, user in enumerate(self):
            if user.get_sciper() not in sciper and \
               user.get_accred_order() != '' or \
               user.get_sciper() in sciper and \
               user.get_accred_order() != '' and \
               user.get_accred_order() < sciper[user.get_sciper()][0]:
                sciper[user.get_sciper()] = (user.get_accred_order(), i)

        list_users = [sciper[user][1] for user in sciper]

        return Users([user for i, user in enumerate(self)
                      if i in list_users])

    def filter_by_scipers(self, scipers):
        """
        Filtre en fonction d'une liste de scipers passés en argument.
        """
        return Users([user for user in self
                      if user.get_sciper() in scipers])

    def filter_by_emails(self, emails):
        """
        Filtre en fonction d'une liste d'emails passés en argument.
        """
        return Users([user for user in self
                      if user.get_email() in emails])

    def get_emails(self, output='string'):
        """
        Retourne une liste d'adresse emails
        """
        txt = ';'.join(list(set([user.get_email()
                                 for user in self
                                 if user.get_email() != ''])))
        if output == 'string':
            return txt
        elif output.endswith('.txt'):
            with open(output, 'w') as f:
                f.write(txt)

    def to_excel(self, file_name):
        """
        Enregistre les données au format Excel.
        """
        df = pd.DataFrame(columns=['Sciper',
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
                                   'Adresse 3'])

        for i, user in enumerate(self):

            # Création des colonnes à partir de l'index de la première série
            if i == 0:
                df = pd.DataFrame(columns=user.get_info().index)

            df = df.append(user.get_info(), ignore_index=True)

        df.to_excel(file_name, index=False)
