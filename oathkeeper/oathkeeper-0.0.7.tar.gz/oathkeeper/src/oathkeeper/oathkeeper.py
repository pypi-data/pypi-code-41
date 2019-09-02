import os
import sys
import requests
import json

class Oathkeeper(object):
    def __init__(self, email, password, environment='default', **redis_kwargs):
        try:
            if len(email) > 0 and len(password) > 0:
                self.EMAIL = email
                self.PASSWORD = password
                self.BASE_URL = "https://accounts-dev.greendeck.co/v1"
                self.API_TOKEN = ""
                self.ENV = environment
                self.HEADERS = {"Content-Type":"application/json", "Authorization":self.API_TOKEN}
                try:
                    body = {
	                   "email": email,
	                   "password": password
                    }
                    payload = json.dumps(body)
                    response = json.loads(requests.request("POST", self.BASE_URL+"/users/signin/", data=payload, headers=self.HEADERS).text)
                    try:
                        api_token = response["token"]
                        if ["success"] and api_token.startswith("Bearer "):
                            self.API_TOKEN = api_token
                            self.HEADERS = {"Content-Type":"application/json", "Authorization":self.API_TOKEN}
                            print("Oathkeeper INFO: "+"Oathkeeper connected.")
                        else:
                            print("Oathkeeper ERROR: "+"Invalid token received. Please enter a valid email and password.")
                    except Exception as e:
                        raise
                except Exception as e:
                    raise
            else:
                print("Oathkeeper ERROR: "+"Email or password is empty. Please enter a valid email and password.")
        except Exception as e:
            print("Oathkeeper ERROR: "+"Error while signing you in. Please enter a valid email and password. "+str(e))
            # raise

    # def delete(self, key):
    #     try:
    #         if self.SECRET is not None and key in self.SECRET:
    #             del self.SECRET[key]
    #             try:
    #                 self.GD_MONGODB_CLIENT_COLLECTION.update_one({"environment":self.ENV}, { "$unset" : { key : 1} })
    #             except Exception as e:
    #                 print("Oathkeeper ERROR: "+str(e))
    #         else:
    #             print("Oathkeeper INFO: "+"Can't find the key *"+key+"* in your oathkeeper.")
    #     except Exception as e1:
    #         print("Oathkeeper ERROR: "+str(e1))


    def set(self, key, value):
        uri_suffix = "/secrets/"+key+"/"+self.ENV+""
        body = {
        "value":value
        }
        payload = json.dumps(body)
        try:
            url = self.BASE_URL+uri_suffix

            response_object = requests.request("POST", url, data=payload, headers=self.HEADERS)

            # Re-authorize
            if "unauthorized" in response_object.text:
                self.__init__(self.EMAIL, self.PASSWORD, self.ENV)
                self.set(key, value)
            # Re-authorize

            response = json.loads(response_object.text)
            if response["success"]:
                print("Oathkeeper INFO: Added key value pair: "+key+": "+str(value)+" to your Oathkeeper Secret for Environment: "+str(self.ENV))
                pass
            else:
                print("Oathkeeper ERROR: Unable to set value for key: "+key+". "+str(e))

        except Exception as e:
            print("Oathkeeper ERROR: Error in processing your request for key: "+key+". "+str(e))

    def get(self, key, default_value=None):
        uri_suffix = "/secrets/"+key+"/"+self.ENV+""
        try:
            url = self.BASE_URL+uri_suffix

            response_object = requests.request("GET", url, headers=self.HEADERS)

            # Re-authorize
            if "unauthorized" in response_object.text:
                self.__init__(self.EMAIL, self.PASSWORD, self.ENV)
                self.get(key)
            # Re-authorize

            response = json.loads(response_object.text)
            if response["success"] and "secret" in response:
                try:
                    return response["secret"]["value"]
                except Exception as e:
                    print("Oathkeeper ERROR: Key: "+key+" not found for Environment: "+str(self.ENV))
                    return default_value
            else:
                print("Oathkeeper ERROR: Key: "+key+" not found for Environment: "+str(self.ENV))
                return default_value
        except Exception as e:
            print("Oathkeeper ERROR: Error in processing your request for key: "+key+". ")
            return default_value
