# -*- coding: utf-8 -*-
import socket

if socket.gethostname() == 'EGG-PC':
    PROFILE = 'dev'
else:
    PROFILE = 'prod'

if PROFILE == 'dev':
    redis_nodes =  [{'host':'192.168.136.130','port':7000},
                    {'host':'192.168.136.130','port':7001},
                    {'host':'192.168.136.130','port':7002},
                    {'host':'192.168.136.131','port':7000},
                    {'host':'192.168.136.131','port':7001},
                    {'host':'192.168.136.131','port':7002},
                    ]
    cache_expires = 30
    # landing = ["hbase","hdfs","es"]
    landing = []
    hbase_host = 'master.hadoop'
    hbase_port = 9090
    accessid = ''
    accesskey = ''
    es_host = ['20.26.26.43', '20.26.25.224', '20.26.25.225']
    # es_host = ["master.hadoop"]
    hdfs_web = "http://master.hadoop:50070"
    hdfs_dir = "/user/spider/cplatform/"
    hdfs_user = "hadoop"
    app_user = {
        'user1':'pwd1',
        'user2':'pwd2'
    }

elif PROFILE == 'prod':
    redis_nodes =  [{'host':'10.78.155.61','port':16340},
                    {'host':'10.78.155.67','port':16340},
                    {'host':'10.78.155.68','port':16340},
                    {'host':'10.78.155.70','port':16340},
                    {'host':'10.78.155.71','port':16340},
                    {'host':'10.78.155.72','port':16340},
                    ]
    cache_expires = 86400
    # landing = ["hbase","hdfs","es"]
    landing = []
    hbase_host = '10.78.138.74'
    hbase_port = 9090
    accessid = '480092febea017febfe4'
    accesskey = '3fe3bccd97e3c8cb9c5b57cffc74090671722641'
    es_host = ['10.78.190.228', '10.78.190.229', '10.78.190.230', '10.78.190.231', '10.78.190.232', '10.78.190.233',
               '10.78.190.234', '10.78.190.235']
    #
    # es_host = ["10.78.138.53",
    #            "10.78.138.54",
    #            "10.78.138.55",
    #            "10.78.138.56",
    #            "10.78.138.57",
    #            "10.78.138.58",
    #            "10.78.138.59",
    #            "10.78.138.60",
    #            "10.78.138.61",
    #            "10.78.138.62",
    #            "10.78.138.63",
    #            "10.78.138.64",
    #            "10.78.138.65",
    #            "10.78.138.66",
    #            "10.78.138.67",
    #            "10.78.138.68",
    #            "10.78.138.69",
    #            "10.78.138.70",
    #            "10.78.138.71",
    #            "10.78.138.72",
    #            ]
    hdfs_web = "http://10.78.138.81:50070"
    hdfs_dir = "/user/spider/cplatform/"
    hdfs_user = "hadoop"
    app_user = {
        'cplatform':'9gw5gXTw',
        'operation_robot':'yjIgAfzF'
    }
