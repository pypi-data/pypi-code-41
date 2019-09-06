# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
# Create your models here.
class ThiThirdApp(models.Model):
    appId = models.CharField(max_length=64,null=False,primary_key=True,default='')
    appKey =  models.CharField(max_length=64,null=False)
    appName =  models.CharField(max_length=64,null=False)

class AccessToken(models.Model):
    accessToken = models.CharField(max_length=64,null=False)
    thiThirdApp = models.ForeignKey(ThiThirdApp, on_delete=models.CASCADE)
    updateTime =  models.DateTimeField()

class UserLoginToken(models.Model):
    loginToken = models.CharField(max_length=64,null=False)
    userName =  models.CharField(max_length=64,null=False)
    displayUserName = models.CharField(max_length=64,null=True)
    updateTime =  models.DateTimeField()
    thiThirdApp = models.ForeignKey(ThiThirdApp,on_delete=models.CASCADE)

class CaeAccount(models.Model):
    thiThirdApp = models.ForeignKey(ThiThirdApp, on_delete=models.CASCADE)
    accountName = models.CharField(max_length=64,null=False)
    userNameSuffix = models.CharField(max_length=32, null=False, default="")
    quota = models.IntegerField(null=False)
    cpuTime = models.IntegerField(null=False)
