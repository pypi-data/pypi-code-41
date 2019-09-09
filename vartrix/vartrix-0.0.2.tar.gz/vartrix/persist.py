# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 17:05:43 2019

@author: Reuben
"""

import ruamel.yaml as yml

class Yaml():
    def load(self, fname):
        with open(fname) as f:
            dct = yml.safe_load(f)
        return dct
    
    def save(self, dct, fname):
        with open(fname) as f:
            yml.safe_write(dct, f)
            
            
handler = Yaml()
load = handler.load
save = handler.save

def set_handler(handler):
    global load, save
    load = handler.load
    save = handler.save
    
automation_handler = Yaml()
automation_load = handler.load
automation_save = handler.save

def set_automation_handler(handler):
    global automation_load, automation_save
    automation_load = handler.load
    automation_save = handler.save
    
            

