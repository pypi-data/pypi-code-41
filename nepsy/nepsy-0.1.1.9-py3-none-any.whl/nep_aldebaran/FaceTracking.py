#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

# Luis Enrique Coronado Zuniga

# You are free to use, change, or redistribute the code in any way you wish
# but please maintain the name of the original author.
# This code comes with no warranty of any kind.

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
import time
import os
import sys

class FaceTracking(ALModule):

    def __init__(self, ip, port):

        self.port = 9559
        self.ip = ip

        self.name = "FaceTrackingEventListener"
        proxy_name = "ALTracker"

        self.tracker = ALProxy("ALTracker",self.ip, self.port)
        self.memory = ALProxy("ALMemory",self.ip, self.port)
        self.targetName = "People"
        self.distanceX = 0.0
        self.distanceY = 0.0
        self.angleWz = 0.0
        self.thresholdX = 0.0
        self.thresholdY = 0.0
        self.thresholdWz = 0.0
        self.effector = "None"
        self.subscribeDone = False
        self.isRunning = False
        self.memory.subscribeToEvent("ALTracker/ActiveTargetChanged", self.name, "onTargetChanged")
        print ( proxy_name + " success")
        

        
    def onUnload(self):
        if self.subscribeDone:
            self.memory.unsubscribeToEvent("ALTracker/TargetLost", self.name)
            self.memory.unsubscribeToEvent("ALTracker/TargetReached", self.name)
            self.subscribeDone = False

        if self.isRunning:
            self.tracker.setEffector("None")
            self.tracker.stopTracker()
            self.tracker.unregisterTarget(self.targetName)
            self.isRunning = False

    def onRun(self, input_ = "People", parameters = {"use_body":"Head", "use_arms":"None"}, parallel = False):

        mode = "Head"
        self.effector ="None"

        try:
            mode = parameters["use_body"]   # "WholeBody", "Move", "Head"
            self.effector = parameters["use_arms"]  #  "None", "Arms", "LArms", "RArms"
        except:
            pass

        self.targetName = input_      #  "Face"
        self.distanceX = 0.3
        self.thresholdX = 0.1
        self.distanceY = 0.0
        self.thresholdY = 0.1
        self.angleWz = 0.0
        self.thresholdWz = 0.3
        

        if self.subscribeDone:
            self.memory.unsubscribeToEvent("ALTracker/TargetLost", self.name)
            self.memory.unsubscribeToEvent("ALTracker/TargetReached", self.name)
            self.subscribeDone = False
        
        self.memory.subscribeToEvent("ALTracker/TargetLost", self.name, "onTargetLost")
        self.memory.subscribeToEvent("ALTracker/TargetReached", self.name, "onTargetReached")
        self.subscribeDone = True

        self.tracker.setEffector(self.effector)
        if input_ == "People":
            peopleIds = []
            self.tracker.registerTarget(self.targetName, peopleIds)
        if input_ == "RedBall":
            diameter = 0.06000
            self.tracker.registerTarget(self.targetName, diameter)
        self.tracker.setRelativePosition([-self.distanceX, self.distanceY, self.angleWz,
                                           self.thresholdX, self.thresholdY, self.thresholdWz])
        self.tracker.setMode(mode)

        self.tracker.track(self.targetName) # Start tracker
        self.isRunning = True

    def onStop(self):
        self.onUnload()

    def onTargetLost(self, key, value, message):
        print ("Target lost")
        #self.targetLost()

    def onTargetReached(self, key, value, message):
        print ("Target reached")
        #self.targetReached()

    def onTargetChanged(self, key, value, message):
        if value == self.targetName and not self.subscribeDone:
            self.memory.subscribeToEvent("ALTracker/TargetLost", self.name, "onTargetLost")
            self.memory.subscribeToEvent("ALTracker/TargetReached", self.name, "onTargetReached")
            self.subscribeDone = True
        elif value != self.targetName and self.subscribeDone:
            self.memory.unsubscribeToEvent("ALTracker/TargetLost", self.name)
            self.memory.unsubscribeToEvent("ALTracker/TargetReached", self.name)
            self.subscribeDone = False




##robot_port = "9559"
##robot_name = "pepper"
##robot_ip = '192.168.0.100'
##middleware = "nanomsg"
##pattern = "survey"
##pip   = robot_ip
##pport = int(robot_port)
##
##
##SpeechEventListener = FaceTracking(robot_ip,pip)
##SpeechEventListener.onRun("People", {"use_body":"Head", "use_arms":"LArm"})
##
##time.sleep(6)
##SpeechEventListener.onStop()
##myBroker.shutdown()

