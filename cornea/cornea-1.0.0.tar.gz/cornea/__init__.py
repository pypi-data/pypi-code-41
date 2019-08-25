import os
import requests
import json

version = "1.0.0"

subscription_key = os.environ.get("AZURE_API_KEY")
assert subscription_key

azure_api_base_endpoint = os.environ.get("AZURE_API_BASE_ENDPOINT")
assert azure_api_base_endpoint

azure_api_version = os.environ.get("AZURE_API_VERSION") or "v2.0"
assert azure_api_version

analyze_url = azure_api_base_endpoint + \
    "/vision/" + azure_api_version + "/analyze"


def descImgFromURL(url):
    '''
    Describe an image from a remote URL.

    @param {String} url URL of the remote image

    @returns {Dictionary} Response from the Azure Computer Vision API
    '''

    if url == "":
        print("Image URL cannot be empty")
    else:
        headers = {'Ocp-Apim-Subscription-Key': subscription_key}
        params = {'visualFeatures': 'Categories,Description,Color'}
        data = {'url': url}
        response = requests.post(analyze_url, headers=headers,
                                 params=params, json=data)
        response.raise_for_status()
        return response.json()


'''
Sample remote image to describe
'''
if __name__ == "__main__":
    descImgFromURL(
        "https://upload.wikimedia.org/wikipedia/commons/b/b9/CyprusShorthair.jpg")
