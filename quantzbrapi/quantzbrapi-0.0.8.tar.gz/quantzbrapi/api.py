import requests
from data_to_pd import quote_to_pandas, carteiras_to_pandas

import json
import pandas as pd 

class API:
    def __init__(self, token):
        self.api = 'http://35.247.226.209:8881'
        self.token = token
        self.headers = {}
        self.headers["Authorization"] = "Token " + self.token 
        self.headers["accept"] = "application/json"

    def _connect(self, uri):
        r = requests.get("{}/{}".format(self.api, uri), headers=self.headers)
        return r

    def cotacoes_diarias(self, ativo):
        connector = "api/cotacao/diario/{}".format(ativo)
        data = self._connect(connector)
        j_data = json.loads(data.text)
        return quote_to_pandas(j_data)
        
    def listar_ativos(self, indice):
        connector = "api/carteiras/{}".format(indice)
        data = self._connect(connector)
        j_data = json.loads(data.text)
        return carteiras_to_pandas(j_data)

