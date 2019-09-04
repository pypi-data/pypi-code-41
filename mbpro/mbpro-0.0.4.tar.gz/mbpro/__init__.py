#python setup.py sdist
#twine upload dist/*
def rand(n1, n2):
	from random import randint
	try:
		a = int(n1)
		b = int(n2)
		return randint(a, b)
	except:
		lista = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
		num = 0
		num2 = 0
		for i in lista:
			if(i == str(n1)):
				break
			else:
				num = num+1
		for x in lista:
			if(x == str(n2)):
				break
			else:
				num2 = num2+1
		return lista[randint(num, num2)]

def pega(s, t, e):
	return (s.split(t)[1]).split(e)[0]

class curl:
	def __init__(self, url, header=False, post=False, timeout=False):
		global data
		global head
		import socket
		import json
		try:
			host = pega(url, '://', '/').split(':')[0]
		except:
			try:
				host = (url.split('/')[0]).split(':')[0]
			except:
				try:
					host = url.split(':')[0]
				except:
					host = url
		try:
			path = (url.split('://')[1]).split('/')[1]
		except:
			try:
				path = url.split('/')[1]
			except:
				path = ''
		try:
			port = pega(url, '://', '/')
			port = port.split(':')[1]
		except:
			try:
				port = int(pega(url, ':', '/'))
			except:
				try:
					port = int(url.split(':')[1])
				except:
					port = 80
		port = int(port)
		heading = f'GET /{path} HTTP/1.1\r\n'
		if(header):
			cont = False
			for i in header:
				if(i == 'content-type'):
					cont = True
				heading = f'{heading}{i}: {header[i]}\r\n'
			if(cont == False):
				heading = f'{heading}content-type: application/x-www-form-urlencoded\r\n'
			heading = f'{heading}\r\n'
		else:
			heading = f'{heading}host: {host}\r\ncontent-type: application/x-www-form-urlencoded\r\n'
		if(post):
			post_bytes = post
			post = f'{post}\r\n\r\n'
			method = 'POST'
			length = f"Content-Length: {str(len(post_bytes))}\r\n\r\n"
			request = f"""\
{heading.replace('GET /', 'POST /')}{length}"""
			request = f'{request}{post_bytes}'
		else:
			method = 'GET'
			request = f'{heading}\r\n'
		try:
			ip = socket.gethostbyname(host)
		except:
			ip = host
		request = request.encode()
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			if(timeout):
				s.settimeout(timeout)
			s.connect((ip, port))
			s.sendall(request)
			result = s.recv(10000000).decode('utf-8')
		except:
			result = 'Maximo de tempo excedido!'
		try:
			data = result.split('\r\n\r\n')[1]
		except:
			data = result
		head = result.split('\r\n\r\n')[0]
	def headers(self):
		try:
			lista = head.split('\r\n')
			lista.remove(lista[0])
			lista.remove(lista[0])
			cara = dict()
			for i in lista:
				i = i.split(':')
				cara[i[0].lower()] = i[1]
			return cara
		except:
			return data
	def text(self):
		return data
	def json(self):
		import json
		return json.loads(data)
	def content(self):
		return data.encode()

def connect(proxy):
	return curl('http://proxy.mbpro.in/chk_proxy.php?proxy={}'.format(proxy)).text()