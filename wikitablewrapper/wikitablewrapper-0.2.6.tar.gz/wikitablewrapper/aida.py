#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'henry'

import subprocess
import urllib.parse
import xmltodict
import pickle

null = None

class Aida:
    url  = "https://gate.d5.mpi-inf.mpg.de/aida/service/disambiguate"
    number_of_request = 5
    key = ""
    lang = "EN"
    
    def __init__(self, l = None):
        if l!=None:
            self.lang = l

    def request_curl(self,text):
        query_post = "text=" + urllib.parse.quote(text)
        for i in range(self.number_of_request):
            try:
                p = subprocess.Popen(['curl', '--data', query_post, self.url],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                stdout, stderr = p.communicate()
                if stdout:
                    self.raw_output = stdout
                    return stdout
            except Exception as err:
                print(err)
                continue
        return None
    
    # Joe_Jackson_\\u0028manager\\u0029   ----->   Joe_Jackson_(manager)
    def decode(self,x):
        x_ = x.replace("\\u00","%")
        return urllib.parse.unquote(x_)
    
    def Yago2lastWiki(self,x):
        return self.decode(x[5:])
    
    
    def annotate(self,text):
        
        if not text:
            print("Error: the text entered is empty!")
            return None

        R = []
        dict_response = eval(self.request_curl(text))
        for entity in dict_response["mentions"]:
            if "bestEntity" in entity:
                last_part_url = self.Yago2lastWiki(entity["bestEntity"]["kbIdentifier"])
                ini = int(entity["offset"])
                fin = int(entity["offset"]) + int(entity["length"])
                R.append({"ini":ini, "fin":fin, "url":last_part_url})
                
        return R
