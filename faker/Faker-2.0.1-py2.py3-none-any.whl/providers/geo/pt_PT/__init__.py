# coding=utf-8

from __future__ import unicode_literals
from .. import Provider as GeoProvider


class Provider(GeoProvider):

    nationalities = (
        "Afegã", "Albanesa", "Arménia", "Angolana", "Argentina", "Austríaca", "Australiana", "Azerbaijã", "Belga",
        "Bulgara", "Boliviana", "Brasileira", "Bielorussa", "Canadiana", "Congolesa (República Democrática do Congo)",
        "Congolesa (República do Congo)", "Suíça", "Marfinense", "Chilena", "Chinesa", "Colombiana", "Costa-Riquenha",
        "Cubana", "Cabo-verdiana", "Cipriota", "Checa", "Alemã", "Dinamarquesa", "Dominicana", "Argelina",
        "Equatoriana", "Estónia", "Egípcia", "Espanhola", "Etíope", "Finlândesa", "Francesa", "Grega",
        "Guineense (Bissau)", "Croata", "Húngara", "Indonésia", "Irlandesa", "Israelita", "Indiana", "Iraquiana",
        "Iraniana", "Islandesa", "Italiana", "Jamaicana", "Japonesa", "Queniana", "Coreana", "Libanesa", "Lituana",
        "Luxemburguesa", "Letã", "Marroquina", "Moldava", "Birmanesa", "Maltesa", "Mexicana", "Moçambicana",
        "Nigeriana", "Holandesa", "Norueguesa", "Nepalesa", "Neozelandesa", "Peruana", "Filipina", "Paquistanesa",
        "Polaca", "Portuguesa", "Paraguaia", "Romena", "Russa", "Ruandesa", "Sudanesa", "Sueca", "Eslovena", "Eslovaca",
        "Senegalesa", "Somali", "Santomense", "Salvadorenha", "Tailandesa", "Tunisina", "Turca", "Ucraniana",
        "Britânica", "Americana", "Uruguaia", "Venezuelana", "Vietnamita", "Sul-Africana", "Sérvia", "Andorrenha",
        "Bósnia", "Camaronesa", "Georgiana", "Ganesa", "Gambiana", "Hondurenha", "Haitiana", "Cazaque", "Libanesa ",
        "Monegasca", "Maliana", "Mongol", "Mauritana", "Malaia", "Panamiana", "Saudita", "Singapurense", "Togolesa",
    )

    def nationality(self):
        """
        :example 'Portuguesa'
        """
        return self.random_element(self.nationalities)
