from ldap3 import Server, Connection, SUBTREE, ALL_ATTRIBUTES
import pickle
import json
from epflldap.users.users import Users
from epflldap.users.user import User


class LdapEpfl:
    SEARCH_BASE = 'o=epfl,c=ch'
    SERVER = 'ldap.epfl.ch'

    def __init__(self, read_from_pickle=False):
        """
        CONSTRUCTEUR:
        Paramètres:
            - read_data_from_pickle: détermine si on charge les données depuis
              un pickle local.
        Action:
            - construit un objet avec l'attribut data
        """
        if read_from_pickle is True:
            self.data = self._read_from_pickle()
        else:
            self.data = self._read_data_from_ldap()

    def _read_data_from_ldap(self):
        """
        Lit les données dans ldap. Retourne les données dans l'attribut data.
        """
        server = Server(LdapEpfl.SERVER)
        conn = Connection(server)
        conn.bind()
        conn.search(LdapEpfl.SEARCH_BASE,
                    '(objectclass=person)',
                    search_scope=SUBTREE,
                    attributes=ALL_ATTRIBUTES)
        self.data = {}
        self.data['persons'] = [json.loads(entry.entry_to_json())
                                for entry in conn.entries]

        conn.search(LdapEpfl.SEARCH_BASE,
                    '(objectclass=organizationalUnit)',
                    search_scope=SUBTREE,
                    attributes=ALL_ATTRIBUTES)

        self.data['units'] = [json.loads(entry.entry_to_json())
                              for entry in conn.entries]

        return self.data

    def _read_from_pickle(self):
        """
        Lit les données enregistrées au format pickle.
        """
        with open('ldap_epfl.pickle', 'rb') as f:
            return pickle.load(f)

    def to_pickle(self):
        """
        Enregistre au format pickle les données. C'est plus rapide que si on
        enregistrait un fichier json.
        """
        with open('ldap_epfl.pickle', 'wb') as f:
            pickle.dump(self.data, f)

    def get_users(self):
        """Retourne la liste des utilisateurs
        """
        return Users([User(pers) for pers in self.data['persons']])
