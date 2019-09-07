#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'henry'

import subprocess
import urllib.parse
import xmltodict
import pickle


class Tagme:
    url  = "https://tagme.d4science.org/tagme/tag"
    number_of_request = 5
    key = "7e442182-f61f-44f9-aff7-b2855796da35-843339462"
    lang = "EN"

    def __init__(self, l = "EN"):
        if not l.lower() in ["en","it","de"]:
            print("ERROR--> TAGME does not support this language")
        self.lang = l

    def request_curl(self,text):
        query_post = "text=" + urllib.parse.quote(text)+ "&lang="+self.lang.lower()+"&gcube-token="+self.key+"&include_categories=true"
        for i in range(self.number_of_request):
            try:
                p = subprocess.Popen(['curl', '--data', query_post, self.url],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                stdout, stderr = p.communicate()
                if stdout:
                    self.raw_output = stdout
                    return stdout
            except Exception as err:
                print(unicode(err))
                continue
        return None

    
    
    def annotate(self,text):
        if not text:
            print("Error: the text entered is empty!")
            return None

        dict_response = eval(self.request_curl(text))
        R = []
        
        for entity in dict_response["annotations"]:
            if "title" in entity:
                last_part_url = entity["title"].replace(" ","_")
                ini = int(entity["start"])
                fin = int(entity["end"]) 
                R.append({"ini":ini, "fin":fin, "url":last_part_url})
        return R


