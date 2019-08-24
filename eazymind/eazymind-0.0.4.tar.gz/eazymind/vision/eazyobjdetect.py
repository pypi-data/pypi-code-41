import requests

class Detector(object):
    def __init__(self,key):
        self.key = key
        self.url = "http://eazymind.herokuapp.com/arabic_sum/eazyobjdetect"

    def run(self, image_data):
        files = {"imagedata":image_data}
        values = {'key':self.key }
        response =  requests.post(self.url , files=files ,data=values )
        return response.content
   