import socket
from threading import Thread
import cv2
import base64
from json import dumps as dictToJson
from json import loads as jsonToDict

RUN_IMG = 'BEGIN_IMAGE'.encode()
END_IMG = 'END_IMAGE'.encode()
STOP = 'STOP'.encode()

class FireEye(Thread):
	def __init__(self, addr='127.0.0.1', port=8080):
		super(FireEye, self).__init__()
		self.addr = addr
		self.port = port
		self.sending = False
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
				if STOP in msg.keys():
					return
				self.channels[msg['type']] = msg['data']
				tmp = ''
			except: continue

	def get(self, channel):
		if channel in self.channels.keys():
			return self.channels[channel]
		return None

	def write(self, channel, data):
		msg = {'type': channel, 'data': data}
		self.client.send(dictToJson(msg).encode())

	def encodeImg(self, img):
		success, encoded_img = cv2.imencode('.png', img)
		return base64.b64encode(encoded_img)

	def writeImg(self, data):
		if not self.sending:
			self._writeImg(data)

	def _writeImg(self, data):
		self.sending = True
		self.client.send(RUN_IMG)
		self.client.send(self.encodeImg(data))
		self.client.send(END_IMG)
		self.sending = False

	def exit(self):
		self.client.send(STOP)
