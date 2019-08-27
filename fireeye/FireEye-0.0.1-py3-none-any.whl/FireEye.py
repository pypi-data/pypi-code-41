import socket
from threading import Thread
import base64
import cv2
from json import dumps as dictToJson
from json import loads as jsonToDict

class FireEye(Thread):
	def __init__(self, addr='127.0.0.1', port=12346):
		super(FireEye, self).__init__()
		self.addr = addr
		self.port = port
		self.channels = {}
		self.open()
		self.start()

	def open(self):
		while True:
			try:
				self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.client.connect((self.addr, self.port))
				return
			except: continue

	def run(self, size=256):
		tmp = ''
		while True:
			tmp += self.client.recv(size).decode().encode('utf-8')
			try:
				msg = jsonToDict(tmp)
				if 'stop' in msg.keys():
					return
				if msg['type'] not in self.channels.keys():
					self.registerChannel(msg['type'])
				self.channels[msg['type']] = msg['data']
				tmp = ''
			except: continue

	def registerChannel(self, channel):
		self.channels[channel] = None

	def get(self, channel):
		if channel in self.channels.keys():
			return self.channels[channel]
		return None

	def write(self, data):
		self.client.send(data)

	def writeImg(self, img):
		success, encoded_img = cv2.imencode('.jpg', img)
		self.client.send('START_IMAGE'.encode())
		self.client.send(base64.b64encode(encoded_img))
		self.client.send('END_IMAGE'.encode())

	def exit(self):
		self.client.send(dictToJson(msg).encode())
