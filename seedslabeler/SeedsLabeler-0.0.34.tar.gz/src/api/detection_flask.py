import requests
import json
import pickle
class FlaskClient(object):
    def __init__(self, host = 'localhost', port = 5000):
        self.host = host
        self.port = port


    def processImageLabels(self, data):
        # print(data.text)
        data_json = json.loads(data.text)
        # return pickle.loads(data.text)
        # print( data_json['boxes'])
        return (data_json['boxes'], data_json['labels_words'], data_json['scores'])


    def sendDetectionImage(self, image_path):
    #  '''sends image in bytes and gets JSON file'''
        try:
            print('Trying to send Image to server')
            if image_path is None:
                print('image path is none')
                return
            im = open(image_path, 'rb')
            image_bytes = im.read()
            print('Read an image')
            x = requests.post(f'http://{self.host}:{self.port}/api/predict', data =  image_bytes, headers = {"content-type": "image/jpeg"})
            print('Send a response')
            return self.processImageLabels(x)

        except Exception as e:
            print("Closed a thread for server", str(e))
            return None
