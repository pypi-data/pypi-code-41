import requests
import json
import re
from robot.api import logger

class Notify:

    ROBOT_LISTENER_API_VERSION = 2
    
    flag = False
    url = "https://slack.com/api/chat.postMessage"
    

    def __init__(self, slackChannel, slackToken, testSuite, buildBy, buildWhy):
        
        self.slackChannel = slackChannel
        self.slackToken = 'Bearer ' + slackToken
        self.testSuite = testSuite
        self.buildBy = buildBy
        self.buildWhy = buildWhy
        self._init_slack_message()
        #self.flag = True


    def _init_slack_message(self):
        self.payload = {}
       

    def end_suite(self, name, result):
        #if self.flag is True:
        #self.suite_name = name
        self.suite_statistics =  result['statistics']
        self.suite_statistics = re.split("\n", self.suite_statistics, 1)
        self.suite_status = result['status']                 
            
    def close(self):
        self._notify_slack()
        
        
    def _notify_slack(self):  
        
        self.headers = {"Authorization":self.slackToken, "Content-Type":"application/json"}   
        
        self.payload['channel'] = self.slackChannel
        
        self.payload['attachments'] =  [{}]
        
        self.payload['attachments'][0]['color'] = '#D3D3D3'
        self.payload['attachments'][0]['blocks'] =  [{},{},{},{},{}]
        
        
        self.payload['attachments'][0]['blocks'][0]['type'] = 'divider'
        self.payload['attachments'][0]['blocks'][1]['type'] = 'context'
        self.payload['attachments'][0]['blocks'][1]['elements'] = [{}]
        self.payload['attachments'][0]['blocks'][1]['elements'][0]['type'] = 'mrkdwn'
        self.payload['attachments'][0]['blocks'][1]['elements'][0]['text'] = '*Test Suite:*'
        
        self.payload['attachments'][0]['blocks'][2]['type'] = 'context'
        self.payload['attachments'][0]['blocks'][2]['elements'] = [{}]
        self.payload['attachments'][0]['blocks'][2]['elements'][0]['type'] = 'mrkdwn'
        self.payload['attachments'][0]['blocks'][2]['elements'][0]['text'] = '*Test Status:*'
        
        
        self.payload['attachments'][0]['blocks'][3]['type'] = 'context'
        self.payload['attachments'][0]['blocks'][3]['elements'] = [{}]
        self.payload['attachments'][0]['blocks'][3]['elements'][0]['type'] = 'mrkdwn'
        self.payload['attachments'][0]['blocks'][3]['elements'][0]['text'] = '*Build Details:*'
        
        
        self.payload['attachments'][0]['blocks'][4]['type'] = 'actions'
        self.payload['attachments'][0]['blocks'][4]['elements'] = [{},{},{}]
        self.payload['attachments'][0]['blocks'][4]['elements'][0]['type'] = 'button' 
        self.payload['attachments'][0]['blocks'][4]['elements'][0]['text'] = {}
        self.payload['attachments'][0]['blocks'][4]['elements'][0]['text']['type'] = 'plain_text'
        self.payload['attachments'][0]['blocks'][4]['elements'][0]['text']['text'] = 'View Metrics'
        self.payload['attachments'][0]['blocks'][4]['elements'][0]['text']['emoji'] = True
        self.payload['attachments'][0]['blocks'][4]['elements'][0]['url'] = 'https://www.google.com/view-metrics' 
        self.payload['attachments'][0]['blocks'][4]['elements'][0]['value'] = 'view-metrics' 
        
        
        self.payload['attachments'][0]['blocks'][4]['elements'][1]['type'] = 'button' 
        self.payload['attachments'][0]['blocks'][4]['elements'][1]['text'] = {}
        self.payload['attachments'][0]['blocks'][4]['elements'][1]['text']['type'] = 'plain_text'
        self.payload['attachments'][0]['blocks'][4]['elements'][1]['text']['text'] = 'View Log'
        self.payload['attachments'][0]['blocks'][4]['elements'][1]['text']['emoji'] = True
        self.payload['attachments'][0]['blocks'][4]['elements'][1]['url'] = 'https://www.google.com/view-log' 
        self.payload['attachments'][0]['blocks'][4]['elements'][1]['value'] = 'view-log' 
        
        
        self.payload['attachments'][0]['blocks'][4]['elements'][2]['type'] = 'button' 
        self.payload['attachments'][0]['blocks'][4]['elements'][2]['text'] = {}
        self.payload['attachments'][0]['blocks'][4]['elements'][2]['text']['type'] = 'plain_text'
        self.payload['attachments'][0]['blocks'][4]['elements'][2]['text']['text'] = 'View Report'
        self.payload['attachments'][0]['blocks'][4]['elements'][2]['text']['emoji'] = True
        self.payload['attachments'][0]['blocks'][4]['elements'][2]['url'] = 'https://www.google.com/view-report' 
        self.payload['attachments'][0]['blocks'][4]['elements'][2]['value'] = 'view-report'
        
        
        testSuite = self.payload["attachments"][0]["blocks"][1]["elements"][0]["text"]
        testSummary = self.payload["attachments"][0]["blocks"][2]["elements"][0]["text"]
        buildDetails = self.payload["attachments"][0]["blocks"][3]["elements"][0]["text"]  
       
        
                
        self.payload["attachments"][0]["blocks"][1]["elements"][0]["text"] = testSuite + " " + self.testSuite
        self.payload["attachments"][0]["blocks"][2]["elements"][0]["text"] = testSummary + " " + self.suite_statistics[1]
        self.payload["attachments"][0]["blocks"][3]["elements"][0]["text"] = buildDetails + " " + "by " + self.buildBy + " - " + self.buildWhy
        
      
        
        if self.suite_status == 'PASS':
            self.payload["attachments"][0]["color"] = "#008000"
        
        else:
            self.payload["attachments"][0]["color"] = "#FF0000"
                 
                     
        response = requests.post(self.url, data=json.dumps(self.payload), headers=self.headers)
        
        if response.status_code == 200:
            logger.info('Slack Notification Passed')
            self.flag = False
            return None
        else:
            logger.error("Slack Notification Failed:", response.status_code, response.reason)
            return None  
