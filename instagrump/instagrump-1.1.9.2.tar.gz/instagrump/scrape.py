from bs4 import BeautifulSoup as soup
import requests, json

def scrape_profile(url):
	data = requests.get(url)
	data = soup(data.text, 'html.parser')
	if 'Page Not Found' not in data.find('title').get_text():
		data = data.find_all('script',{'type':'text/javascript'})[-12].get_text()
		data = data.replace('window._sharedData = ','').replace(';','')
		try:
			return json.loads(data)
		except:
			print(data)
			raise
	return False

def scrape_avatar(url):
	data = requests.get(url)
	data = soup(data.text, 'html.parser')
	data = data.find('a', {'class':'instadp-post'}).find('img').get('src')
	return data

def scrape_stories(url):
	data = requests.get(url)
	data = soup(data.text, 'html.parser')
	data = data.find('ul', {'class':'stories-list'})
	if data:
		data = data.find_all('li', {'class':'story'})
	return data