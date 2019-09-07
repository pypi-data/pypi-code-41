#!/usr/bin/python3
# -*- coding: utf-8 -*-

####/usr/bin/env python
__author__ = 'henry'

import subprocess
##Python2:import urllib
import urllib.parse
import xmltodict
import pickle
import os

class Freme_NER:
    url  = "https://api.freme-project.eu/current/e-entity/freme-ner/documents?"
    number_of_request = 5
    lang = "EN"

    def __init__(self, l = "EN"):
        if not l.lower() in ["en","de","fr","es","it"]:
            print("ERROR--> FREME-NER does not support this language")
        self.lang = l

    def request_curl(self,text):
        for i in range(self.number_of_request):
            try:
                text = text.replace("'"," ")
                command = "curl -X POST --header 'Content-Type: text/plain' --header 'Accept: text/turtle' -d '"+text+"' 'https://api.freme-project.eu/current/e-entity/freme-ner/documents?language=%s&dataset=dbpedia&mode=all'"%(self.lang.lower())
                #print(command)
                p = os.popen(command,"r")
                output = ""
                while True:
                    line = p.readline()
                    if not line: break
                    output += line
                return output
            except Exception as err:
                print(unicode(err))
                continue
        return None
        
    def getBetween(self,txt,t1,t2):
        p1 = txt.find(t1)
        if (p1 == -1):
            return -1
        
        s = txt[p1+len(t1):]
        p2 = s.find(t2)
        if (p2 == p1-1):
            return -1
        
        
        return s[:p2]
        


    def annotate(self,text):
        if not text:
            print("Error: the text entered is empty!")
            return None
        
        
        R = []
        response = self.request_curl(text)

        ch = ""
        for l in response.split("\n"):
            line = l.strip(" \n")
            if not line: continue

            if line.find("@prefix")!=-1: continue;
            if line[-1] != ".":
                ch = ch + line;
            else:
                ch = ch + line + "\n";
                if ch.find("nif:Phrase") != -1:  # annotacion
                    p1 = ch.find('itsrdf:taIdentRef')
                    if p1!=-1:
                        last_part_url = self.getBetween(ch[p1:],"<",">").split("/")[-1]
                        
                        p1 = ch.find('nif:endIndex')
                        fin = int(self.getBetween(ch[p1:], '"', '"'))
                        
                        
                        p1 = ch.find('nif:beginIndex')
                        ini = int(self.getBetween(ch[p1:], '"', '"'))
                        
                        R.append({"ini":ini, "fin":fin, "url":last_part_url})
                        
                elif ch.find("nif:sourceUrl") != -1: # documents
                    pass
                
                elif ch.find("nif:broaderContext") != -1: # sentencia
                    pass
                ch = ""
                        
        return R



