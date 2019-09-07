#!/usr/bin/python3
# -*- coding: utf-8 -*-

####/usr/bin/env python
__author__ = 'henry'

import subprocess
import urllib.parse
import xmltodict
import pickle


class Babelfy:
    url  = "https://babelfy.io/v1/disambiguate"
    number_of_request = 5
    key = "c6d8a6d4-c919-42f8-80da-ccf124975145"
    #key="807038db-4b34-4656-b1f0-54b1792d7dee"
    lang = "EN"
    todos = True


    def __init__(self, l = "EN", todos_ = None):
        self.lang = l        
        if (todos_!=None):
            self.todos = todos_

    def request_curl(self,text):
        if self.todos:
            query_post = "lang="+self.lang+"&key="+self.key+"&annType=ALL&text="+urllib.parse.quote(text)#(text.encode("utf8"))
        else: query_post = "lang="+self.lang+"&key="+self.key+"&annType=NAMED_ENTITIES&text="+urllib.parse.quote(text)#(text.encode("utf8"))

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
    
    
    def getSamePosition(self,tag,v,A):
        L_ = []
        for a in A:
            if a[tag] == v:
                L_.append(a)
        return L_

    def onlyMaximalAnnotations(self, _R_): # non-overlapping
        final = []
        
        oldpos = -1
        R = sorted(_R_, key=lambda x:x["ini"], reverse=False)
        for i in range(len(R)):
            r = R[i]
            if r["ini"] > oldpos:
                L = self.getSamePosition("ini", r["ini"],R)
                L_s = sorted(L, key=lambda x:x["fin"], reverse=True)
                final.append(L_s[0])
                oldpos = r["fin"]            
        
        return final


    def annotate(self,text):
        if not text:
            print("Error: the text entered is empty!")
            return None

        R = []
        req = self.request_curl(text)

        list_response = eval(req)
        for entity in list_response:
            if "DBpediaURL" in entity and entity["DBpediaURL"]:
                last_part_url = entity["DBpediaURL"].split("/")[-1]
                ini = int(entity["charFragment"]["start"])
                fin = int(entity["charFragment"]["end"]) + 1
                R.append({"ini":ini, "fin":fin, "url":last_part_url})
        return self.onlyMaximalAnnotations(R)


