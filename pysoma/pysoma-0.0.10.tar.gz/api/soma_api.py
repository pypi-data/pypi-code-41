import requests

class SomaApi:
    timeout = 5

    def __init__(self, soma_connect_ip, soma_connect_port):
        self.soma_connect_ip = soma_connect_ip
        self.soma_connect_port = soma_connect_port

    def list_devices(self):
        return requests.get(url = "http://"+self.soma_connect_ip+":"+str(self.soma_connect_port)+"/list_devices", timeout = self.timeout).json()
    
    def open_shade(self, mac):
        return requests.get(url = "http://"+self.soma_connect_ip+":"+str(self.soma_connect_port)+"/open_shade/"+mac, timeout = self.timeout).json()
    
    def close_shade(self, mac):
        return requests.get(url = "http://"+self.soma_connect_ip+":"+str(self.soma_connect_port)+"/close_shade/"+mac, timeout = self.timeout).json()
    
    def stop_shade(self, mac):
        return requests.get(url = "http://"+self.soma_connect_ip+":"+str(self.soma_connect_port)+"/stop_shade/"+mac, timeout = self.timeout).json()
    
    def get_shade_state(self, mac):
        return requests.get(url = "http://"+self.soma_connect_ip+":"+str(self.soma_connect_port)+"/get_shade_state/"+mac, timeout = self.timeout).json()
    
    def set_shade_position(self, mac, position):
        return requests.get(url = "http://"+self.soma_connect_ip+":"+str(self.soma_connect_port)+"/set_shade_position/"+mac+"/"+str(position), timeout = self.timeout).json()
    
    def get_battery_level(self, mac):
        return requests.get(url = "http://"+self.soma_connect_ip+":"+str(self.soma_connect_port)+"/get_battery_level/"+mac, timeout = self.timeout).json()
