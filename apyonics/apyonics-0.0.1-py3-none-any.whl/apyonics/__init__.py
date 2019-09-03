import requests

class Client(object):

    def __init__(self,service_url,api_key):
        super(Client,self).__init__()
        test_url = service_url+'test_connection'
        resp = requests.get(test_url, headers={'Api-Key':api_key})
        if resp.json()['response'] == 'connected to aionics service':
            self.service_url = service_url
            self.api_key = api_key
        else:
            raise RuntimeError('unable to connect to aionics service')

    def get_candidate_features(self,mpid):
        resp = requests.get(
            self.service_url+'feature_set_candidate', 
            params={'mpid_query':mpid},
            headers={'Api-Key':self.api_key}
        )
        return resp.json()

    def get_candidate_conductivity(self,mpid):
        resp = requests.get(
            self.service_url+'predict_conductivity_in_candidate', 
            params={'mpid_query':mpid},
            headers={'Api-Key':self.api_key}
        )
        return resp.json()

    def get_trainingset_features(self,formula):
        resp = requests.get(
            self.service_url+'feature_set_trainingset', 
            params={'chemical_formula_query':formula},
            headers={'Api-Key':self.api_key}
        )
        return resp.json()

    def get_trainingset_conductivity(self,formula):
        resp = requests.get(
            self.service_url+'conductivity_trainingset', 
            params={'chemical_formula_query':formula},
            headers={'Api-Key':self.api_key}
        )
        return resp.json()

    def predict_from_poscar(self,poscar_path):
        resp = requests.post(
            self.service_url+'predict_from_poscar',
            files={'poscar':open(poscar_path)},
            headers={'Api-Key':self.api_key}
        )
        return resp.json()

