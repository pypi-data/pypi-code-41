import requests

class SomaApi:
    def __init__(self, soma_connect_ip):
        self.soma_connect_ip = soma_connect_ip

    def list_devices(self):
        return requests.get(url = "http://"+self.soma_connect_ip+":3000/list_devices").json()['shades']
    
    def open_shade(self, mac):
        return requests.get(url = "http://"+self.soma_connect_ip+":3000/open_shade/"+mac).json()['result']
    
    def close_shade(self, mac):
        return requests.get(url = "http://"+self.soma_connect_ip+":3000/close_shade/"+mac).json()['result']
    
    def get_shade_state(self, mac):
        return requests.get(url = "http://"+self.soma_connect_ip+":3000/get_shade_state/"+mac).json()
    
    def set_shade_position(self, mac, position):
        return requests.get(url = "http://"+self.soma_connect_ip+":3000/set_shade_position/"+mac+"/"+str(position)).json()['result']
    
    def get_battery_level(self, mac):
        return requests.get(url = "http://"+self.soma_connect_ip+":3000/get_battery_level/"+mac).json()
