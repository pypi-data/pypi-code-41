from __future__ import print_function

import json
import time
import requests


class IntellihubClient:
    """
        This is Intellihub Python SDK Client for v1.2.0.
        For more information, visit https://intellihub.ai/documentation/

        Attributes:
            api_key (str): API Key Generated for an app in Intellihub.
    """

    def __init__(self, api_key):
        """
            The constructor for Intellihub Client.

            Parameters:
                api_key (str): API Key Generated for an app in Intellihub.

            Returns:
                IntellihubClient: Client object for Intellihub.
        """
        self.api_key = api_key
        self.base_url = "https://intellihub.ai/api/v1"

    def sentiment_analysis(self, text):
        """
            The function to call sentiment analysis service in Phoenix Language.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-language/

        :param str text: The text on which sentiment analysis is to be applied.
        :return:
            obj:A json obj containing sentiment analysis response.
        """

        body = {'text': text}
        body = json.dumps(body)
        url = self.base_url + '/language-service/phoenix-language/nlp/sentiment/'
        headers = {'ApiKey': self.api_key, 'Content-type': 'application/json'}
        response = requests.post(url=url, data=body, headers=headers)
        print(response.text)
        return response

    def pos_tagger(self, text):
        """
            The function to call pos tagger service in Phoenix Language.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-language/

        :param str text: The text on which POS analysis is to be applied.
        :return
            obj: A json obj containing POS tagger response.
        """

        body = {'text': text}
        body = json.dumps(body)
        url = self.base_url + '/language-service/phoenix-language/nlp/pos/'
        headers = {'ApiKey': self.api_key, 'Content-type': 'application/json'}
        response = requests.post(url=url, data=body, headers=headers).json()
        return response

    def ner_tagger(self, text):
        """
            The function to call ner tagger service in Phoenix Language.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-language/

        :param str text: The text on which NER Tagger is to be applied.
        :return
            obj: A json obj containing NER tagger response.
        """

        body = {'text': text}
        body = json.dumps(body)
        url = self.base_url + '/language-service/phoenix-language/nlp/ner/'
        headers = {'ApiKey': self.api_key, 'Content-type': 'application/json'}
        response = requests.post(url=url, data=body, headers=headers).json()
        return response

    def dependency_parser(self, text):
        """
            The function to call dependency parser service in Phoenix Language.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-language/

        :param str text: The text on which Dependency Parser is to be applied.
        :return
            obj: A json obj containing dependency Parser response.
        """

        body = {'text': text}
        body = json.dumps(body)
        url = self.base_url + '/language-service/phoenix-language/nlp/dependency-parser/'
        headers = {'ApiKey': self.api_key, 'Content-type': 'application/json'}
        response = requests.post(url=url, data=body, headers=headers).json()
        return response

    def tags(self, text):
        """
            The function to call tags extractor service in Phoenix Language.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-language/

        :param str text: The text on which tags is to be applied.
        :return
            obj: A json obj containing tags response.
        """

        body = {'text': text}
        body = json.dumps(body)
        url = self.base_url + '/language-service/phoenix-language/nlp/tags/'
        headers = {'ApiKey': self.api_key, 'Content-type': 'application/json'}
        response = requests.post(url=url, data=body, headers=headers).json()
        return response

    # phoenix-vision

    def face_detection_image(self, image_path):
        """
            The function to call face detection service in Phoenix Vision.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-vision/

        :param str image_path: The path of the image file.
        :return
            text : A base64 decoded image with face detected.
        """

        body = {'image': (image_path, open(image_path, 'rb'), 'multipart/form-data')}
        url = self.base_url + '/vision-service/phoenix-vision/face-detection/image'
        headers = {'ApiKey': self.api_key}
        response = requests.post(url=url, files=body, headers=headers)
        return response.content

    def face_detection_json(self, image_path):
        """
            The function to call face detection service in Phoenix Vision.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-vision/

        :param str image_path: The path of the image file.
        :return
            obj : A list of co-ordinates for all faces detected in the image.
        """
        body = {'image': (image_path, open(image_path, 'rb'), 'multipart/form-data')}
        url = self.base_url + '/vision-service/phoenix-vision/face-detection/json'
        headers = {'ApiKey': self.api_key}
        response = requests.post(url=url, files=body, headers=headers).json()
        return response

    def object_detection_image(self, image_path):
        """
            The function to call object detection service in Phoenix Vision.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-vision/

        :param str image_path: The path of the image file.
        :return
            text : A base64 decoded image with objects detected.
        """
        body = {'image': (image_path, open(image_path, 'rb'), 'multipart/form-data')}
        url = self.base_url + '/vision-service/phoenix-vision/object-detection/image'
        headers = {'ApiKey': self.api_key}
        response = requests.post(url=url, files=body, headers=headers)
        return response.content

    def object_detection_json(self, image_path):
        """
            The function to call object detection service in Phoenix Vision.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-vision/

        :param str image_path: The path of the image file.
        :return
            obj : A list of co-ordinates for all objects detected in the image.
        """
        body = {'image': (image_path, open(image_path, 'rb'), 'multipart/form-data')}
        url = self.base_url + '/vision-service/phoenix-vision/object-detection/json'
        headers = {'ApiKey': self.api_key}
        response = requests.post(url=url, files=body, headers=headers).json()
        return response

    def image_classification(self, image_path):
        """
            The function to call image classification service in Phoenix Vision.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-vision/

        :param str image_path: The path of the image file.
        :return
            obj : A list of all classes detected in the image.
        """
        body = {'image': (image_path, open(image_path, 'rb'), 'multipart/form-data')}
        url = self.base_url + '/vision-service/phoenix-vision/image-classification'
        headers = {'ApiKey': self.api_key}
        response = requests.post(url=url, files=body, headers=headers).json()
        return response

    def custom_image_clf_train(self, name, zip_folder_url, images_column, labels_column, train_percentage, epochs, steps_per_epoch):
        """
            The function to call custom image classification service in Phoenix Vision.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-vision/

        :param str name: name of the service.
        :param str zip_folder_url: url of uploaded images zip folder with csv file.
        :param str images_column: column name of images in csv file. it is case sensitive
        :param str labels_column: column name of labels in csv file. it is case sensitive
        :param float train_percentage: % of data will be used for training and model will be tested against remaining % of data.
        :param int epochs: number of iterations on over all data while training.
        :param int steps_per_epoch: no of images take into account for each iteration.
        :return
            obj : A json obj containing job info which is created by this api.
        """
        body = {
            'service': 'classification',
            'name': name,
            'zipFolderUrl': zip_folder_url,
            'imagesColumn': images_column,
            'labelsColumn': labels_column,
            'trainPercentage': train_percentage,
            'epochs': epochs,
            'stepsPerEpoch': steps_per_epoch
        }
        body = json.dumps(body)
        url = self.base_url + '/vision-service/phoenix-vision/custom-image-classification/train'
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.post(url=url, data=body, headers=headers).json()
        return response

    def custom_image_clf_predict(self, name, zip_folder_url, model_url):
        """
            The function to call custom image classification service in Phoenix Vision.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-vision/

        :param str name: name of the service.
        :param str zip_folder_url: url of uploaded test images zip folder.
        :param str model_url: url of model trained.
        :return
            obj : A json obj containing job info which is created by this api.
        """
        body = {
            'service': 'classification',
            'name': name,
            'zipFolderUrl': zip_folder_url,
            'modelUrl': model_url,
        }
        body = json.dumps(body)
        url = self.base_url + '/vision-service/phoenix-vision/custom-image-classification/predict'
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.post(url=url, data=body, headers=headers).json()
        return response

    def custom_image_clf_predict_image(self, model_url, image_path):
        """
            The function to call custom image classification service in Phoenix Vision.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-vision/

        :param str model_url: url of model trained.
        :param str image_path: path of the image.
        :return
            obj : A json obj containing classes predicted by trained model.
        """
        file = {'image': (image_path, open(image_path, 'rb'), 'multipart/form-data')}
        body = {'modelUrl': model_url}
        body=json.dumps(body)
        url = self.base_url + '/vision-service/phoenix-vision/custom-image-classification/predict/image'
        headers = {'ApiKey': self.api_key}
        response = requests.post(url=url, files=file, data=body, headers=headers)
        return response

    def custom_object_detection_train(self, name, zip_folder_url, images_column, labels_column, train_percentage, steps):
        """
            The function to call custom object detection service in Phoenix Vision.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-vision/

        :param str name: name of the service.
        :param str zip_folder_url: url of uploaded images zip folder with csv file.
        :param str images_column: column name of images in csv file. it is case sensitive
        :param str labels_column: column name of labels in csv file. it is case sensitive
        :param float train_percentage: % of data will be used for training and model will be tested against remaining % of data.
        :param int steps: no of images take into account for each iteration.
        :return
            obj : A json obj containing job info which is created by this api.
        """
        body = {
            'name': name,
            'zipFolderUrl': zip_folder_url,
            'imagesColumn': images_column,
            'labelsColumn': labels_column,
            'trainPercentage': float(train_percentage),
            'steps': int(steps)
        }
        body = json.dumps(body)
        url = self.base_url + '/vision-service/phoenix-vision/custom-object-detection/train'
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.post(url=url, data=body, headers=headers).json()
        return response

    def custom_object_detection_predict(self, name, zip_folder_url, model_url):
        """
            The function to call custom object detection service in Phoenix Vision.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-vision/

        :param str name: name of the service.
        :param str zip_folder_url: url of uploaded test images zip folder.
        :param str model_url: url of model trained.
        :return
            obj : A json obj containing job info which is created by this api.
        """
        body = {
            'name': name,
            'zipFolderUrl': zip_folder_url,
            'modelUrl': model_url,
        }
        body = json.dumps(body)
        url = self.base_url + '/vision-service/phoenix-vision/custom-object-detection/predict'
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.post(url=url, data=body, headers=headers).json()
        return response

    def custom_object_detection_predict_image(self, model_url, image_path):
        """
            The function to call custom object detection service in Phoenix Vision.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-vision/

        :param str model_url: url of model trained.
        :param str image_path: path of the image.
        :return
            obj : A base64 encoded string of the image containing objects detected by trained model.
        """
        body = {'image': (image_path, open(image_path, 'rb'), 'multipart/form-data')}
        data={'modelUrl': model_url}
        body=json.dumps(body)
        url = self.base_url + '/vision-service/phoenix-vision/custom-object-detection/predict/image'
        headers = {'ApiKey': self.api_key}
        response = requests.post(url=url, files=body, data=data, headers=headers)
        return response.content

    def custom_object_detection_predict_json(self, model_url, image_path):
        """
            The function to call custom object detection service in Phoenix Vision.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-vision/

        :param str model_url: url of model trained.
        :param str image_path: path of the image.
        :return
            obj : A json obj containing objects detected by trained model.
        """
        body = {'image': (image_path, open(image_path, 'rb'), 'multipart/form-data')}
        data = {'modelUrl': model_url}
        body=json.dumps(body)
        url = self.base_url + '/vision-service/phoenix-vision/custom-object-detection/predict/json'
        headers = {'ApiKey': self.api_key}
        response = requests.post(url=url, files=body, data=data, headers=headers).json()
        return response

    def vision_job_status(self, job_id):
        """
            The function call to get the job status in Phoenix Vision.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-vision/

        :param int job_id: jobId from the train api response.
        :return:
            obj: A json obj containing the status details.
        """
        url = self.base_url + '/vision-service/phoenix-vision/status/{0}'.format(job_id)
        JOB_STATUS_CHECK_INTERVAL = 5
        STATE = 'status'
        headers = {'ApiKey': self.api_key}
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            response = response.json()
            if response[STATE] == "RUN":
                while response[STATE] == 'FINISH' or response[STATE] == 'FAIL':
                    time.sleep(JOB_STATUS_CHECK_INTERVAL)
                    response = requests.get(url=url, headers=headers).json()
            if response[STATE] == 'FAIL':
                raise Exception('job failed!')
            return response
        else:
            raise Exception('Error while checking the status. Got ' + str(response.status_code))

    def text_to_speech(self, text, gender):
        """
            The function call to get the Text from Speech  in Phoenix Conversation.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-conversation/

        :param str text: the text on which tts is to be applied.
        :param str gender: text to speech supports 'MALE' , 'FEMALE' or 'NEUTRAL'
        :return:
            obj: A audio content obj which can be written into a audio file.
        """
        body = {'text': text, 'gender': gender}
        body = json.dumps(body)
        url = self.base_url + '/conversation-service/phoenix-conversation/text-to-speech/'
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.post(url=url, data=body, headers=headers)
        return response.content

    def speech_to_text(self, audio_path):
        """
            The function call to get the  Speech from text in Phoenix Conversation.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-conversation/

        :param str audio_path: the path of the audio file.
        :return:
            obj: A json obj containing transcript of the audio file.
        """
        body = {'audio': (audio_path, open(audio_path, 'rb'), 'multipart/form-data')}
        url = self.base_url + '/conversation-service/phoenix-conversation/speech-to-text/'
        headers = {'ApiKey': self.api_key}
        response = requests.post(url=url, files=body, headers=headers).json()
        return response

    def translation(self, text, language):
        """
            The function call to get the  translation of text  in Phoenix Conversation.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-conversation/

        :param str text: the text on which tts is to be applied.
        :param str language: target language code.
        :return:
            obj: A json obj containing transcript of the text translated into target language.
        """
        body = {
            'text': text,
            'language': language
        }
        body = json.dumps(body)
        url = self.base_url + '/conversation-service/phoenix-conversation/translation/'
        headers = {'ApiKey': self.api_key}
        response = requests.post(url=url, data=body, headers=headers).json()
        return response

    def emotion_analysis(self, video_file_url, name, description):
        """
            The function call to get average of emotions in a video using phoenix tape.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-tape/

        :param str video_file_url: the path of the video file uploaded into spotflock storage.
        :param str name: name by which job is saved.
        :param str description: description of the job.
        :return:
            obj: A json obj containing job details created by this api.
        """
        body = {
            'fileUrl': video_file_url,
            'name': name,
            'description': description
        }
        body = json.dumps(body)
        url = self.base_url + '/tape-service/phoenix-tape/emotion-analysis/'
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.post(url=url, data=body, headers=headers).json()
        return response

    def tape_status(self, job_id):
        """
            The function call to get the job status  using phoenix tape.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-tape/

        :param int job_id: the job id of the task created by emotion_analysis api.
        :return:
            obj: A json obj containing status and output of job.
        """
        url = self.base_url + '/tape-service/phoenix-tape/job/get/{0}'.format(job_id)
        JOB_STATUS_CHECK_INTERVAL = 5
        STATE = 'status'
        headers = {'ApiKey': self.api_key}
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            response = response.json()
            if response[STATE] == "RUN":
                while response[STATE] == 'FINISH' or response[STATE] == 'FAIL':
                    time.sleep(JOB_STATUS_CHECK_INTERVAL)
                    response = requests.get(url=url, headers=headers).json()
            if response[STATE] == 'FAIL':
                raise Exception('job failed!')
            return response
        else:
            raise Exception('Error while checking the status. Got ' + str(response.status_code))

    def sarcasm_analysis(self, text):
        """
            The function to call Sarcasm Analysis service in Phoenix Content Inspector.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-content-inspector/

        :param str text: the text on which sarcasm analysis is done.
        :return:
            obj: A json obj containing % of sarcasm and non-sarcasm.
        """
        body = {'text': text}
        body = json.dumps(body)
        url = self.base_url + '/content-inspector-service/phoenix-content-inspector/sarcasm/'
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.post(url=url, data=body, headers=headers).json()
        return response

    def abuse_analysis(self, text):
        """
            The function to call Abusive Analysis service in Phoenix Content Inspector.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-content-inspector/

        :param str text: the text on which abusive analysis is done.
        :return:
            obj: A json obj representing class into which text is classified. This api supports hate, offensive speech and neutral classes.
        """
        body = {'text': text}
        body = json.dumps(body)
        url = self.base_url + '/content-inspector-service/phoenix-content-inspector/abuse-analysis/'
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.post(url=url, data=body, headers=headers)
        print(response.text)
        return response.json()

    def create_chatbot(self, name, type_):
        """
            The function to call chatbot service in cloud chatbot.
            For more information, visit https://intellihub.ai/docs/ai/chatbot/

        :param str name: the name of the chatbot.
        :param str type_: type of the chatbot. 'flow' or 'default'.
        :return:
            obj: A json obj containing the info of the chatbot.
        """
        url = self.base_url + '/chatbot-service/cloud-chatbot/'
        body = {
            'name': name,
            'type': type_,
            'basic_conversation': {
                'doubtful_text': "Sorry. I didn't get you.Could you rephrase that?",
                'welcome_text': "Hey buddy! How can I help you?",
                'seeoff_text': "Happy to help you.Will see you soon!"
            },
            'social_webhooks': {},
            'facebook_recipient_id': ""
        }
        if type_ == 'flow':
            body['flow_conversation'] = {
                'api_config': {
                    'url': 'http://someurl.here/api/v1/api_path'
                },
                'questions': [
                    {
                        "question": "Hello, I'm flow based chatbot. May I know your name?",
                        "responseType": "input_text",
                        "jsonKey": "name",
                        "order": 1
                    },
                    {
                        "question": "I can be useful for collecting information from user. Sometimes filling a long form can be tiresome, right?",
                        "responseType": "input_text",
                        "jsonKey": "boolean_value",
                        "order": 2
                    },
                    {
                        "question": "I can make that process quick and easy.",
                        "responseType": "input_text",
                        "jsonKey": "process_info",
                        "order": 3
                    }
                ]
            }
        elif type_ == 'default':
            body['entities'] = []
            body['intents'] = []
        headers = {'ApiKey': self.api_key}
        body=json.dumps(body)
        response = requests.post(url=url, headers=headers, json=body)
        if response.status_code == "200":
            return response.json()
        else:
            print(response)
            print(response.text)

    def get_chatbot_by_id(self):
        """
            The function to call chatbot service in cloud chatbot.
            For more information, visit https://intellihub.ai/docs/ai/chatbot/

            Note: only one chatbot is created per app.
        :return:
            obj: A json obj containing chatbot info.
        """
        url = self.base_url + '/chatbot-service/cloud-chatbot/'
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def add_entity(self, name, items):
        """
            The function to call chatbot service in Phoenix Vision.
            For more information, visit https://intellihub.ai/docs/ai/chatbot/

        :param str name: the name of the entity.
        :param list items: list of items to be added.
        :return:
            obj: A json obj stating either entities added successfully or not.
        """
        url = self.base_url + '/chatbot-service/cloud-chatbot/entity/'
        body = {
            'name': name,
            'items': items
        }
        body = json.dumps(body)
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.post(url=url, headers=headers, data=body)
        if response.status_code == 200:
            return response.json()

    def add_intent(self, intent, prompt_entity, prompt_response, response):
        """
            The function to call chatbot service in cloud chatbot.
            For more information, visit https://intellihub.ai/docs/ai/chatbot/
        :param str intent: intent to be added.
        :param str prompt_entity: name of prompt entity.
        :param str prompt_response: response of prompt entity.
        :param str response: default response.
        :return:
            obj: A json obj stating either intents added successfully or not.
        """
        url = self.base_url + '/chatbot-service/cloud-chatbot/intent/'
        body = {
            'intent': intent,
            'prompt-entity': prompt_entity,
            'prompt-response': prompt_response,
            'response': response,
        }
        headers = {"ApiKey": self.api_key}
        body=json.dumps(body)
        response = requests.post(url=url, json=body, headers=headers)
        if response.status_code == 200:
            return response.json()

    def add_flow(self, questions, app_config_url, method):
        """
            The function to call chatbot service in cloud chatbot.
            For more information, visit https://intellihub.ai/docs/ai/chatbot/

        :param list questions: the list of questions to be added.
        :param str app_config_url: the url of the app config.
        :param str method:request  method of the app url.
        str question: question to be added.
        list options: list of options for questions
        str input: type of input for question like number ,text etc.,
        str jsonKey: key to which question is mapped.
        int order: order of question.
        :return:
            obj: A json obj stating either questions added successfully or not.
        """
        url = self.base_url + '/chatbot-service/cloud-chatbot/flow/'
        questions_list = []
        for question in questions:
            if 'options' in question.keys():
                questions_list.append({'question': question['question'],
                                       'options': question['options'],
                                       'jsonKey': question['jsonKey'],
                                       'order': question['order']})
            elif 'input' in question.keys():
                questions_list.append({'question': question['question'],
                                       'input': question['input'],
                                       'jsonKey': question['jsonKey'],
                                       'order': question['order']})

        body = {
            'questions': questions_list,
            'api-config': {
                'url': app_config_url,
                'method': method
            }
        }
        body = json.dumps(body)
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.post(url=url, headers=headers, data=body)
        if response.status_code == 200:
            return response.json()

    def get_flow(self):
        """
            The function to call chatbot service in cloud chatbot.
            For more information, visit https://intellihub.ai/docs/ai/chatbot/
        :return:
            obj: A json obj containing flow is returned.
        """
        url = self.base_url + '/chatbot-service/cloud-chatbot/flow/'
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            return response.json()

    def converse_suggestion(self, item, entity):
        """
            The function to call chatbot service in cloud chatbot.
            For more information, visit https://intellihub.ai/docs/ai/chatbot/
        :param str item:item to be added.
        :param str entity: the entiy of the item.
        :return:
            obj: A json obj stating either converse is updated or not.
        """
        url = self.base_url + '/chatbot-service/cloud-chatbot/converse/'
        body = {
            'item': item,
            'entity': entity,
        }
        body = json.dumps(body)
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.get(url=url, headers=headers, data=body)
        if response.status_code == 200:
            return response.json()

    def update_converse_suggestion(self, welcome_text, doubtful_text, seeoff_text):
        """
            The function to call chatbot service in cloud chatbot.
            For more information, visit https://intellihub.ai/docs/ai/chatbot/

        :param str welcome_text: updating welcome text.
        :param str doubtful_text: updating doubtful text.
        :param str seeoff_text: updating seeoff text.
        :return:
            obj: A json obj stating either converse is updated or not.
        """
        url = self.base_url + '/chatbot-service/cloud-chatbot/ml/chatbot/converse/'
        body = {
            'welcome_text': welcome_text,
            'doubtful_text': doubtful_text,
            'seeoff_text': seeoff_text
        }
        body = json.dumps(body)
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.post(url=url, headers=headers, data=body)
        if response.status_code == 200:
            return response.json()

    def converse(self, query):
        """
           The function to call chatbot service in cloud chatbot.
            For more information, visit https://intellihub.ai/docs/ai/chatbot/
        :param str query: query for converse.
        :return:
            obj: A json obj containing response for the query.
        """
        url = self.base_url + '/chatbot-service/cloud-chatbot/ml/chatbot/converse/'
        body = {
            'query': query
        }
        body = json.dumps(body)
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.get(url=url, headers=headers, data=body)
        if response.status_code == 200:
            return response.json()

    def enable_social_webhooks(self, access_token, recipient_id, platform):
        """
            The function to call chatbot service in cloud chatbot.
            For more information, visit https://intellihub.ai/docs/ai/chatbot/
        :param str access_token: access token of the platform .
        :param str recipient_id: recipient id .
        :param str platform: currently supports 'facebook'.
        :return:
            obj: A json obj stating whether chatbot is enabled for platform or not.
        """
        url = self.base_url + '/chatbot-service/cloud-chatbot/social/enable/'
        body = {
            'access_token': access_token,
            'recipient_id': recipient_id,
            'platform': platform
        }
        body = json.dumps(body)
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.post(url=url, headers=headers, data=body)
        if response.status_code == 200:
            return response.json()

    def disable_social_webhooks(self, platform):
        """
            The function to call chatbot service in cloud chatbot.
            For more information, visit https://intellihub.ai/docs/ai/chatbot/

        :param str platform: currently supports 'facebook'.
        :return:
            obj: A json obj stating whether chatbot is disabled for platform or not.
        """
        url = self.base_url + '/chatbot-service/cloud-chatbot/ml/chatbot/social/disable/'
        body = {
            'platform': platform
        }
        body = json.dumps(body)
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.post(url=url, headers=headers, data=body)
        if response.status_code == 200:
            return response.json()

    def train(self, service, algorithm, dataset_url, label, features, model_name=None, lib="weka", train_percentage=80,
              save_model=True, params=None):
        """
            The function call to train service in Phoenix ML.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-ml/

        :param lib: Library for training the model. Currently we are supporting spotflock and weka libraries.
        :param service: Valid parameter values are classification, regression.
        :param model_name: Model name and with this name model will be saved.
        :param algorithm: algorithm by which model will be trained.
        :param dataset_url: dataset file location in spotflock storage.
        :param label: label of the column in dataset file.
        :param train_percentage: % of data will be used for training and model will be tested against remaining % of data.
        :param features: column name list which is used to train classification model.
        :param save_model: If true model will saved in.
        :param params: additional parameters.
        :return:
            obj: A json obj containing model info.

        """
        url = self.base_url + '/ml-service/phoenix-ml/' + service + '/train/'
        headers = {"ApiKey": self.api_key, "Content-type": "application/json"}
        if params is None:
            params = {}
        if model_name is None:
            model_name = algorithm
        body = {
            "library": lib,
            "task": "train",
            "config": {
                "name": model_name,
                "algorithm": algorithm,
                "datasetUrl": dataset_url,
                "label": label,
                "trainPercentage": train_percentage,
                "features": features,
                "saveModel": save_model,
                "params": params
            }
        }
        body=json.dumps(body)
        response = requests.post(url=url, data=body, headers=headers)
        response = response.json()
        return response

    def feedback(self, service, algorithm, train_data, feedback_data, job_id, model_url, label, features, lib='weka',
                 model_name=None, split_perc=80, save_model=True, params=None):
        """
         The function call to feedback service in Phoenix ML.

        :param lib: Trained model's library
        :param service: Trained model's service.
        :param model_name: Trained model's name.
        :param algorithm: Trained model's algorithm.
        :param train_data: Trained model's dataset url.
        :param feedback_data:
                a)Dataset (used for feedback) file location in spotflock storage.
                b)Feedback dataset upload. IMP: Please ensure the dataset has all features used for training the model.
        :param job_id: Job_id from training API response.
        :param model_url: Model file location in spotflock storage.
        :param label: Trained model's label.
        :param split_perc: % of data will be used for training and model will be tested against remaining % of data.
        :param features: Trained model's features.
        :param save_model:If true model will saved in.
        :param params: Additional parameters.
        :return:
            A json obj containing feedback model info.
        """

        url = self.base_url + '/ml-service/phoenix-ml/' + service + '/feedback'

        headers = {'ApiKey': self.api_key, 'Content-type': 'application/json'}

        if params is None:
            params = {}
        if model_name is None:
            model_name = algorithm

        body = {
            'library': lib,
            'service': service,
            'task': 'FEEDBACK',
            'config': {
                'jobId': job_id,
                'name': model_name,
                'algorithm': algorithm,
                'datasetUrl': train_data,
                'feedbackDatasetUrl': feedback_data,
                'modelUrl': model_url,
                'label': label,
                'trainPercentage': split_perc,
                'features': features,
                'saveModel': save_model,
                'params': params
            }
        }
        body=json.dumps(body)
        response = requests.post(url=url, data=body, headers=headers)
        return response.json()

    def predict(self, service, dataset_url, model_url, lib='weka', params=None):
        """
             The function call to predict service in Phoenix ML.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-ml/

        :param lib: Library for training the model. Currently we are supporting spotflock and weka libraries.
        :param service: Valid parameter values are classification, regression.
        :param dataset_url: dataset file location in spotflock storage.
        :param model_url: trained model location in spotflock storage.
        :param params:
        :return:
            obj: A json obj containing the file info which has the predictions.
        """
        url = self.base_url + '/ml-service/phoenix-ml/' + service + '/predict'
        headers = {'ApiKey': self.api_key, 'Content-type': 'application/json'}
        if params is None:
            params = {}
        body = {
            'library': lib,
            # 'service': service,
            'config': {
                'datasetUrl': dataset_url,
                'modelUrl': model_url,
                'params': params
            }
        }
        body=json.dumps(body)
        response = requests.post(url=url, data=body, headers=headers).json()
        return response

    def cluster(self, service, algorithm, dataset_url, features, lib='weka', number_of_clusters=2, model_name=None,
                save_model=True, params=None):
        """
            The function call to cluster service in Phoenix ML.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-ml/

        :param lib: Library for clustering the model. Currently we are supporting spotflock, weka, H2O, scikit-learn
                    libraries. Valid values for this parameter: spotflock, weka, h2o, scikit
        :param service: Valid parameter values are CLUSTER.
        :param model_name: Model name and with this name model will be saved.
        :param algorithm: algorithm by which model will be trained.
        :param epsilon: epsilon is algorithm specific constant.
        :param dataset_url: dataset file location in spotflock storage.
        :param features: column name list which is used to train classification model.
        :param number_of_clusters: the dataset will be clustered into number of clusters.
        :param save_model: If true model will saved
        :param params:
        :return:
            obj: A json obj containing model info.
        """
        url = self.base_url + '/ml-service/phoenix-ml/cluster/'
        headers = {'ApiKey': self.api_key, 'Content-type': 'application/json'}
        if params is None:
            params = {}
        if model_name is None:
            model_name = algorithm
        body = {
            'library': lib,
            'task': 'CLUSTER',
            'service': service,
            'config': {
                'name': model_name,
                'algorithm': algorithm,
                'datasetUrl': dataset_url,
                'numOfClusters': int(number_of_clusters),
                'epsilon': 0.1,
                'features': features,
                'saveModel': save_model,
                'params': params
            }
        }
        body=json.dumps(body)
        response = requests.post(url=url, data=body, headers=headers)
        response = response.json()
        return response

    def job_status(self, job_id):
        """
            The function call to get the job status in Phoenix ML.
            For more information, visit https://intellihub.ai/docs/ai/phoenix-ml/

        :param job_id: jobId from the train api response.
        :return:
            obj: A json obj containing the status details.
        """
        url = self.base_url + '/ml-service/phoenix-ml/job/status?id={0}'.format(job_id)
        JOB_STATUS_CHECK_INTERVAL = 5
        STATE = 'state'
        headers = {'ApiKey': self.api_key}
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            response = response.json()
            while response[STATE] == 'RUN':
                time.sleep(JOB_STATUS_CHECK_INTERVAL)
                response = requests.get(url=url, headers=headers).json()
            if response[STATE] == 'FAIL':
                raise Exception('Prediction job failed!')
        else:
            raise Exception('Error while checking the status. Got ' + str(response.status_code))
        return response

    def job_output(self, job_id):
        """
                The function call to get the job output in Phoenix ML.
                For more information, visit https://intellihub.ai/docs/ai/phoenix-ml/

        :param job_id: job id from the train api response.
        :return:
            obj: A json obj containing the job output details.
        """

        url = self.base_url + '/ml-service/phoenix-ml/output/findBy?jobId={0}'.format(job_id)
        headers = {'ApiKey': self.api_key}
        response = requests.get(url=url, headers=headers)
        return response.json()

    def store(self, file_path):
        """
             The function call to store in Phoenix ML.
             For more information, visit https://intellihub.ai/docs/ai/phoenix-ml/

        :param file_path: The path of the dataset file.
        :return:
            obj: A json obj containing the file path in storage.
        """
        url = self.base_url + '/storage-service/cloud-storage/s3/file'
        headers = {'ApiKey': self.api_key}
        files = {'file': open(str(file_path), 'rb')}
        response = requests.post(url=url, headers=headers, files=files, verify=False)
        response = response.json()
        return response

    def download(self, file_url):
        """
                The function call to download the prediction file in Phoenix ML.
                For more information, visit https://intellihub.ai/docs/ai/phoenix-ml/


        :param file_url: location url of file stored in cloud storage.
        :return:
            txt:  file content in simple text format.
        """
        url = self.base_url + '/storage-service/cloud-storage/s3/file?url={0}'.format(file_url)
        headers = {'ApiKey': self.api_key}
        response = requests.get(url=url, headers=headers)
        return response

    def create_stream(self, name, description):
        """
            The function call to create stream in Darwin.
            For more information, visit https://intellihub.ai/docs/bi/darwin/

       :param name: name of the stream.
       :param description: description of the stream.
       :return:
           obj: A json obj containing info of the stream created.
       """
        url = self.base_url + '/process-service/darwin-process/stream'
        url = "http://139.59.3.59:8080/api/v1/process-service/darwin-process/stream"
        body = {
          "name": name,
          "description": description
        }
        headers = {"ApiKey": self.api_key}
        body=json.dumps(body)
        response = requests.post(url=url, headers=headers, json=body)
        return response

    def configure_dapi_events(self, events):
        """
            The function call to configure dapi events in Darwin.
            For more information, visit https://intellihub.ai/docs/bi/darwin/

       :param events: The events to be configured.
       eventId: Field Identifier
       field: Event Name
       type: Field Type( text/Integer/Long/Float)
       description: Field description
       :return:
           obj: A json obj containing details of dapi events.
       """
        url = self.base_url + '/ingester-service/darwin-ingester/ingester/events/add'
        events_list = []
        for event in events:
            events_list.append({
                'eventId': event['eventId'],
                'field': event['field'],
                'type': event['type'],
                'description': event['description']
            })

        headers = {'ApiKey': self.api_key}
        response = requests.post(url=url, headers=headers, data=events)
        return response

    def configure_ingester(self, source, tags):
        """
            The function call to configure ingester in Darwin.
            For more information, visit https://intellihub.ai/docs/bi/darwin/

       :param source: Source to ingest from (TWIITER/FACEBOOK/DAPI/INSTAGRAM/YOUTUBE).
       :param tags: list of properties of the source.
       configData: Metadata and properties of the source
       :return:
           obj: A json obj containing details of ingester created.
       """
        if tags.dtype() is list:
            url = self.base_url + '/ingester-service/darwin-ingester/config/add'
            body = {
                'source': source,
                'configData': {
                    'tags': tags,
                },
            }
            body = json.dumps(body)
            headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
            response = requests.post(url=url, headers=headers, data=body)
            return response

    def configure_transformer(self, name, description, schema):
        """
            The function call to configure transformer in Darwin.
            For more information, visit https://intellihub.ai/docs/bi/darwin/

       :param str name: Name of the transformer.
       :param str description: Description of the transformer.
       :param jsonObj schema: schema of the jolt transformer object.
       transformer: Jolt Transformer Object.
       :return:
           obj: A json obj containing details of transformer.
       """
        url = self.base_url + '/transformer-service/darwin-transformer/transform'
        body = {
            'name': name,
            'description': description,
            'transformer': {
                'schema': schema
            }
        }
        body = json.dumps(body)
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.post(url=url, headers=headers, data=body)
        return response

    def configure_sink(self, destination, is_enabled):
        """
            The function call to configure sink in Darwin.
            For more information, visit https://intellihub.ai/docs/bi/darwin/

       :param destination: Destination to dump data(POSTGRES/INFLUXDB).
       :param is_enabled: True or False.
       :return:
           obj: A json obj containing details of sink.
       """
        url = self.base_url + '/sink-service/darwin-sink/sink/config'
        body = {
            'destination': destination,
            'isEnabled': is_enabled
        }
        body = json.dumps(body)
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.post(url=url, headers=headers, data=body)
        return response

    def sink_status(self):
        """
            The function call to get sink status in Darwin.
            For more information, visit https://intellihub.ai/docs/bi/darwin/
       :return:
           obj: A json obj containing details of sink.
       """
        url = self.base_url + '/sink-service/darwin-sink/sink/config/status/all'
        headers = {'ApiKey': self.api_key}
        response = requests.get(url=url, headers=headers)
        return response

    def create_process_definition(self, name, description, repeat, repeat_interval, workflow, from_="", to=""):
        """
            The function call to create process definition in Darwin.
            For more information, visit https://intellihub.ai/docs/bi/darwin/

       :param name: The path of the dataset file.
       :param description: Description of the Process Definition
       :param repeat: True or False based on if repeating
       :param repeat_interval: Interval of repeating
       :param from_:
       :param to:
       :param workflow: List of nodes
       :return:
           obj: A json obj containing details of process.
       """
        url = self.base_url + '/process-service/darwin-process/process-definition'
        body = {
              'name' : name,
              'description' : description,
              'repeat' : repeat,
              'repeatInterval' : repeat_interval,
              'from' : from_,
              'to' : to,
              'workflow': workflow
        }
        body = json.dumps(body)
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.post(url=url, headers=headers, data=body)
        return response

    def schedule_process_execution(self):
        """
            The function call to schedule process execution in Darwin.
            For more information, visit https://intellihub.ai/docs/bi/darwin/
       :return:
           obj: A json obj status of scheduled process.
       """
        url = self.base_url + '/process-service/darwin-process/process-execution/schedule'
        headers = {'ApiKey': self.api_key}
        response = requests.post(url=url, headers=headers)
        return response

    def start_process_execution(self):
        """
            The function call to start process in Darwin.
            For more information, visit https://intellihub.ai/docs/bi/darwin/
       :return:
           obj: A json obj status of process started.
       """
        url = self.base_url + '/process-service/darwin-process/process-execution/start'
        headers = {'ApiKey': self.api_key}
        response = requests.post(url=url, headers=headers)
        return response

    def stop_process_execution(self):
        """
            The function call to stop process in Darwin.
            For more information, visit https://intellihub.ai/docs/bi/darwin/
       :return:
           obj: A json obj status of process stopped.
       """
        url = self.base_url + '/process-service/darwin-process/process-execution/stop'
        headers = {'ApiKey': self.api_key}
        response = requests.post(url=url, headers=headers)
        return response

    def unshedule_process_execution(self):
        """
            The function call to unschedule process in Darwin.
            For more information, visit https://intellihub.ai/docs/bi/darwin/
       :return:
           obj: A json obj status of process stopped.
       """
        url = self.base_url + '/process-service/darwin-process/process-execution/unschedule'
        headers = {'ApiKey': self.api_key}
        response = requests.post(url=url, headers=headers)
        return response

    def query_data(self, query, destination):
        """
            The function call to query data  in Darwin.
            For more information, visit https://intellihub.ai/docs/bi/darwin/
        :param query: sql query on the dataset
        :param destination: destination of the dump data.
       :return:
           obj: A json obj containing details of fetched data by above query.
       """
        url = self.base_url + 'process-service/darwin-process/process-sink'
        body={
            'query': query,
            'destination': destination
        }
        body = json.dumps(body)
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.post(url=url, headers=headers, data=body)
        return response

    def create_ipfs_node(self, name, service):
        """
            The function call to create ipfs node in block-ipfs
            For more information, visit https://intellihub.ai/docs/blockchain/block-ipfs/
        :param name: Name of the node
        :param service: Description of the node
       :return:
           obj: A json obj containing details of node created.
       """
        url = self.base_url + '/ipfs-service/cloud-ipfs/node'
        body={
            'name': name,
            'service': service
        }
        body = json.dumps(body)
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.post(url=url, headers=headers, data=body)
        return response.json()

    def get_node_info(self, node_id):
        """
            The function call to get ipfs node info in block-ipfs
            For more information, visit https://intellihub.ai/docs/blockchain/block-ipfs/
        :param node_id: Id of the node
       :return:
           obj: A json obj containing details of node.
       """
        url = self.base_url + '/ipfs-service/cloud-ipfs/node/{0}'.format(node_id)
        headers = {'ApiKey': self.api_key}
        response = requests.get(url=url, headers=headers).json()
        return response

    def get_peers_info(self, node_id):
        """
            The function call to get peers info in block-ipfs
            For more information, visit https://intellihub.ai/docs/blockchain/block-ipfs/
        :param node_id: Id of the node
       :return:
           obj: A json obj containing details of peers connected to this node.
       """
        url = self.base_url + '/ipfs-service/cloud-ipfs/peers-info/{0}'.format(node_id)
        headers = {'ApiKey': self.api_key}
        response = requests.get(url=url, headers=headers).json()
        return response

    def add_file(self, file_path, node_id):
        """
            The function call to add file in block-ipfs
            For more information, visit https://intellihub.ai/docs/blockchain/block-ipfs/
        :param node_id: Id of the node.
        :param file_path: Path of the file.
       :return:
           obj: A json obj containing details of file created.
       """
        url = self.base_url + '/ipfs-service/cloud-ipfs/file/{0}'.format(node_id)
        body = {'file': (file_path, open(file_path, 'rb'), 'multipart/form-data')}
        headers = {'ApiKey': self.api_key}
        response = requests.post(url=url, headers=headers, files=body).json()
        return response

    def get_files(self, node_id):
        """
            The function call to get files in block-ipfs
            For more information, visit https://intellihub.ai/docs/blockchain/block-ipfs/
        :param node_id: Id of the node
       :return:
           obj: A json obj containing details of all files uploaded to this node.
       """
        url = self.base_url + '/ipfs-service/cloud-ipfs/files/{0}'.format(node_id)
        headers = {'ApiKey': self.api_key}
        response = requests.get(url=url, headers=headers).json()
        return response

    def add_device(self, name, description, event_interval):
        """
            The function call to add device in cloud IOT.
            For more information, visit https://intellihub.ai/docs/iot/iot-platform/

       :param name: Name of the device.
       :param description: description for the device.
       :param event_interval: 5s or 1m or 2h or 3d.Interval of time at which device is sending data.m-minutes,h-hours,s-seconds,d-days
       :return:
           obj: A json obj containing the id of the device added.
       """
        url = self.base_url + '/iot-service/cloud-iot/device'
        body = {
            'name': name,
            'description': description,
            'eventInterval': event_interval
        }
        body=json.dumps(body)
        headers = {'ApiKey': self.api_key}
        response = requests.post(url=url, headers=headers, json=body)
        if response.status_code == 200:
            return response.text

    def get_device(self, device_id):
        """
            The function call to get device in cloud IOT.
            For more information, visit https://intellihub.ai/docs/iot/iot-platform/

       :param device_id: Id of the device.
       :return:
           obj: A json obj containing the details of the device.
       """
        url = self.base_url + '/iot-service/cloud-iot/device/{0}'.format(device_id)
        headers = {'ApiKey': self.api_key}
        response = requests.get(url=url, headers=headers)
        return response

    def add_dashboard(self, name, description):
        """
            The function call to add dashboard in cloud IOT.
            For more information, visit https://intellihub.ai/docs/iot/iot-platform/

       :param name: name of the dashboard.
       :param description: Description for the dashboard.
       :return:
           obj: A json obj containing the id of the dashboard added.
       """
        url = self.base_url + '/iot-service/cloud-iot/dashboard'
        body = {
            'name': name,
            'description': description
        }
        body = json.dumps(body)
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.post(url=url, headers=headers, data=body)
        if response.status_code == 200:
            return response.text

    def get_dashboard(self, dashboard_id):
        """
            The function call to get dashboard in cloud IOT.
            For more information, visit https://intellihub.ai/docs/iot/iot-platform/

       :param dashboard_id: Id of the dashboard.
       :return:
           obj: A json obj containing the details of the dashboard.
       """
        url = self.base_url + '/iot-service/cloud-iot/dashboard/{0}'.format(dashboard_id)
        headers = {'ApiKey': self.api_key}
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            return response.json()

    def add_widget(self, name, description, type_, resource, device_id, dashboard_id):
        """
            The function call to add widget in cloud IOT.
            For more information, visit https://intellihub.ai/docs/iot/iot-platform/

       :param name: name of the widget
       :param description: Description for the widge.
       :param type_: TEXT or TIMESERIESGRAPH
       :param resource: Temperature(you need to add this same resource in your device code.)
       :param dashboard_id: dashboard Id.
       :param device_id: device Id
       :return:
           obj: A json obj containing the details of the widget.
       """
        url = self.base_url + '/iot-service/cloud-iot/widget'
        body = {
            'name': name,
            'description': description,
            'type': type_,
            'resource': resource,
            'device':{
                'id': device_id
            },
            'dashboard':{
                'id': dashboard_id
            }
        }
        body = json.dumps(body)
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.post(url=url, headers=headers, data=body)
        if response.status_code == 200:
            return response.json()

    def get_widget_data(self, widget_id, name, description, type_, resource, device, dashboard, time_period):
        """
            The function call get widget in cloud IOT.
            For more information, visit https://intellihub.ai/docs/iot/iot-platform/

        :param widget_id: id of the widget
       :param name: name of the widget
       :param description: Description for the widge.
       :param type_: TEXT or TIMESERIESGRAPH
       :param resource: Temperature(you need to add this same resource in your device code.)
       :param dashboard: dashboard details obtained from response by using add dashboard api.
       :param device: dashboard details obtained from response by using add device api.
       :param time_period: time period to fetch data from the widget. 1d(should give none for TEXT widget)
       :return:
           obj: A json obj containing the details of the widget.
       """
        url = self.base_url + '/iot-service/cloud-iot/widget/data'
        body = {
            'widget':{
                'id':widget_id,
                'name': name,
                'description': description,
                'type': type_,
                'resource': resource,
                'device':{
                    'id': device['id'],
                    'userId': device['userId'],
                    'name': device['name'],
                    'description': device['description'],
                   'appId': device['appId']
                },
                'dashboard':{
                    'id': dashboard['id'],
                    'userId': dashboard['userId'],
                    'name': dashboard['name'],
                    'description': dashboard['description'],
                    'appId': dashboard['appId'],
                    'eventInterval':dashboard['eventInterval']
                },
            },
            'timePeriod': time_period
        }
        body = json.dumps(body)
        headers = {'ApiKey': self.api_key, 'Content-Type': 'application/json'}
        response = requests.post(url=url, headers=headers, data=body)
        if response.status_code == 200:
            return response.json()