import socket
from threading import Thread, Lock
import cv2
import base64
from json import dumps as dictToJson
from json import loads as jsonToDict

STOP = 'STOP'.encode()
ACK = 'ACK'
NEWLINE = '\n'.encode()
IMG_MSG_S = '{"type": "image", "data": "'.encode()
IMG_MSG_E = '"}'.encode()

class FireEye(Thread):
	def __init__(self, addr='127.0.0.1', port=8080):
		super(FireEye, self).__init__()
		self.addr = addr
		self.port = port
		self.canWrite = True
		self.channels = {}
		self.lock = Lock()
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
			tmp += self.client.recv(size).decode()
			try:
				msg = jsonToDict(tmp)
				if STOP in msg.keys():
					self.client.close()
					return
				self.channels[msg['type']] = msg['data']
				if(msg['type'] == ACK):
					self.canWrite = True
				tmp = ''
			except: continue

	def get(self, channel):
		if channel in self.channels.keys():
			return self.channels[channel]
		return None

	def encodeImg(self, img):
		success, encoded_img = cv2.imencode('.png', img)
		return base64.b64encode(encoded_img)

	def writeLock(self, channel, data):
		with self.lock:
			self.write(channel, data)

	def write(self, channel, data):
		if self.canWrite:
			self.canWrite = False
			msg = {'type': channel, 'data': data}
			self.client.sendall(dictToJson(msg).encode() + NEWLINE)

	def writeImgLock(self, data):
		with self.lock:
			self.writeImg(data)

	def writeImg(self, data):
		if self.canWrite:
			self.canWrite = False
			msg = IMG_MSG_S + self.encodeImg(data) + IMG_MSG_E
			self.client.sendall(msg + NEWLINE)

	def exit(self):
		self.client.send(STOP)
