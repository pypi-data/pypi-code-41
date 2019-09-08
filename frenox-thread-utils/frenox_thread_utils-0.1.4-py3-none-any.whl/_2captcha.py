import requests

ID = 1
# RUN = True
class CaptchaService:
	def __init__(self, key, sitekey, url):
		self.id = ID
		self.key= key
		self.data =  {
					'key' 		: key,
					'method' 	: 'userrecaptcha',
					'googlekey' : sitekey,
					'pageurl' 	: url,
					'json' 		: '1'
				}

	def get(self):
		s = requests.Session()
		try:
		 	r = s.post("http://2captcha.com/in.php", params=self.data)
		 	r = r.json()
		 	res_ID = r['request']
		 	while True:
		 		try:
			 		r = s.get("http://2captcha.com/res.php?key={0}&action=get&id={1}&json=1".format(self.key, res_ID))
			 		r = r.json()
			 		if r['status'] != 0:
			 			return r['request']
		 		except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.ConnectTimeout):
			 		print("connnection error, retrying")
		 		except Exception as e:
		 			raise e
		except Exception as e:
		 	print(e)