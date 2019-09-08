import requests, sys

proxies = None

def get_proxies(path="proxies.txt"):
	global proxies
	try:
		with open(path, 'r') as file:
			contents = file.readlines()
			for i, x in enumerate(contents):
				if x.lower() == 'none':
					contents[i] = 'none'
				else:
					x = x.strip()
					if x.count(":") > 2:
						x = x.rsplit(":", 3)
					else:
						x = x.rsplit(":", 1)
					# print(x)
					if len(x) == 4:
						contents[i] = x[2] + ":" + x[3] + "@" + x[0] + ":" + x[1]
					elif len(x) == 2:
						contents[i] = x[0] + ":" + x[1]
					else:
						print("wrong format:", x.join(":"))
			# so this saves the proxies in here and also returns it
			proxies = contents
			return contents
	except Exception as e:
		print("error in processing proxies: ", e)
	sys.exit()

def get_proxy():
	"""
		linear proxy rotation
	"""
	global proxies, iter_proxies
	try:
		return next(iter_proxies)
	except:
		if proxies:
			iter_proxies = iter(proxies)
			return next(iter_proxies)
		else:
			print("proxies pool is not created")
			return None

def get_session(headers=None, proxy=None):
	s = requests.Session()

	#check if header is specified, if not then use default
	if headers:
		try:
			s.headers.update(headers)
		except:
			raise Exception("get_session error: wrong header format")
	else:
		s.headers.update({
			'accept'             		: '*/*',
			'accept-language'    		: 'en-US,en;q=0.9',
			'dnt'                		: '1',
			'user-agent'         		: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
			})

	if proxy:
		if "none" in proxy:
			pass
		elif "socks5://" in proxy:
			s.proxies.update({
					'http' : 'socks5h://'+  proxy.replace("socks5://",""),
					'https': 'socks5h://'+ proxy.replace("socks5://","")
				})
		else:
			s.proxies.update({
					'http' : 'http://'+  proxy.replace("http://",""),
					'https': 'https://'+ proxy.replace("http://","")
				})
	return s

def change_proxy(s, proxy):
	try:
		if "none" in proxy:
			pass
		elif "socks5://" in proxy:
			s.proxies.update({
					'http' : 'socks5h://'+  proxy.replace("socks5://",""),
					'https': 'socks5h://'+ proxy.replace("socks5://","")
				})
		else:
			s.proxies.update({
					'http' : 'http://'+  proxy.replace("http://",""),
					'https': 'https://'+ proxy.replace("http://","")
				})
		return s
	except Exception as e:
		raise e
	return s
