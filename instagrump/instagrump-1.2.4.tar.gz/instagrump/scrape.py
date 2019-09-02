from bs4 import BeautifulSoup as soup
import requests, json

def scrape_profile(url):
	data = requests.get(url)
	data = soup(data.text, 'html.parser')
	if 'Page Not Found' not in data.find('title').get_text():
		data = data.find_all('script', {'type':'text/javascript'})
		for item in data:
			if 'sharedData = {"config"' in item.get_text():
				data = item
				break
		data = data.get_text().replace('window._sharedData = ','').replace(';','')
		return json.loads(data)['entry_data']['ProfilePage'][0]
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