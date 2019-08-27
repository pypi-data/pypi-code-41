#!/usr/bin/python3
# coding=utf8
'''测试程序'''
import get_ip

'''测试图像显示，以及动作组调用'''
import cv2
import time
import LSC_Client
import threading
# ip = get_ip.postaddress()
# stream = "http://"+ip+":8080/?action=stream?dummy=param.mjpg"
# cap = cv2.VideoCapture(stream)
lsc = LSC_Client.LSC_Client()


def Move():
    lsc.MoveServo(6, 1500, 1000)
    lsc.MoveServo(7, 1500, 1000)
    time.sleep(1.1)

    lsc.RunActionGroup(0, 1)
    lsc.WaitForFinish(20000)
    lsc.RunActionGroup(1, 5)

    lsc.WaitForFinish(40000)
    lsc.RunActionGroup(2, 5)
    lsc.WaitForFinish(40000)
    # -------------------------------------------------------
    lsc.RunActionGroup(3, 1)
    lsc.WaitForFinish(20000)
    lsc.RunActionGroup(4, 1)
    lsc.WaitForFinish(30000)
    # lsc.RunActionGroup(5, 1)#前翻要翻车
    # lsc.WaitForFinish(40000)
    # lsc.RunActionGroup(6, 1)#后翻也要翻车
    # lsc.WaitForFinish(40000)
    lsc.RunActionGroup(7, 1)
    lsc.WaitForFinish(60000)
    # lsc.RunActionGroup(8, 1)#仰卧起坐也要翻车
    # lsc.WaitForFinish(60000)
    lsc.RunActionGroup(9, 1)
    lsc.WaitForFinish(60000)
    lsc.RunActionGroup(10, 1)
    lsc.WaitForFinish(60000)
    lsc.RunActionGroup(11, 1)
    lsc.WaitForFinish(60000)
    lsc.RunActionGroup(12, 1)
    lsc.WaitForFinish(60000)
    # lsc.RunActionGroup(13, 1)#大鹏展翅容易翻车
    # lsc.WaitForFinish(60000)
    lsc.RunActionGroup(13, 1)
    lsc.WaitForFinish(60000)
    # lsc.RunActionGroup(14, 1)#下蹲要翻车的
    # lsc.WaitForFinish(60000)
    lsc.RunActionGroup(15, 1)
    lsc.WaitForFinish(60000)
    # lsc.RunActionGroup(16, 1)#街舞
    # lsc.WaitForFinish(60000)
    # lsc.RunActionGroup(17, 1)#江南style
    # lsc.WaitForFinish(60000)
    lsc.RunActionGroup(18, 1)#小苹果
    lsc.WaitForFinish(60000)
    # lsc.RunActionGroup(19, 1)#La Song 舞
    # lsc.WaitForFinish(60000)
    # lsc.RunActionGroup(20, 1)#倍儿爽舞蹈
# 作为子线程开启
# th1 = threading.Thread(target=Move)
# th1.setDaemon(True)
# th1.start()

Move()
# while True:  # 图像显示
#     if cap.isOpened():
#         ret, orgFrame = cap.read()
#         if ret:
#             cv2.imshow("orgFrame", orgFrame)
#             cv2.waitKey(1)
#         else:
#             time.sleep(0.01)
#     else:
#         time.sleep(0.01)
