import requests
from bs4 import BeautifulSoup as soup
from time import sleep

PUBLIC_ENDP = 'https://www.instagram.com/{}?__a=1'
USER_INFO_ENDP = 'https://i.instagram.com/api/v1/users/{}/info'
SCRAPE_URL = 'https://www.instadp.com/{}/{}'
HEADER = {
	'Host': 'www.instagram.com',
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Language': 'en-US,en;q=0.5',
	'Accept-Encoding': 'gzip, deflate, br',
	'Connection': 'keep-alive',
	'Upgrade-Insecure-Requests': '1',
	'Cache-Control': 'max-age=0',
	'TE': 'Trailers'
}

class Profile:

	def __init__(self, username):

		self.data = requests.get(PUBLIC_ENDP.format(username), headers=HEADER)
		sleep(0.2)
		self.data = self.data.json()['graphql']['user']
		self.id = self.data['id']
		self.logging_page_id = 'profilePage_'+self.id
		self.meta_url = USER_INFO_ENDP.format(self.id)
		self.name = self.data['full_name']
		self.username = self.data['username']
		self.is_private = self.data['is_private']
		self.posts = self.data['edge_owner_to_timeline_media']
		self.igtvs = self.data['edge_felix_video_timeline']
		self.posts_length = self.posts['count']
		self.is_verified = self.data['is_verified']
		self.following = self.data['edge_follow']['count']
		self.follower = self.data['edge_followed_by']['count']
		self.biography = self.data['biography']
		self.external_url = self.data['external_url']
		self.is_business_account = self.data['is_business_account']
		self.is_joined_recently = self.data['is_joined_recently']

	def __len__(self):
		return self.posts_length

	def __str__(self):
		data = str("{}\n".format(self.username)
				  +"{}\n".format(self.name)
				  +"Followers: {:,}\n".format(self.follower)
				  +"Following: {:,}\n".format(self.following)
				  +"Posts: {:,}\n".format(self.__len__()))
		data += "Stories: "
		if self.is_private:
			data += "Private\n"
		else:
			storylen = self.get_stories_scraping()
			if storylen:
				data += "{}\n".format(len(storylen))
			else:
				data += "0\n"
		if self.biography:
			data += "Biography:\n{}\n".format(self.biography)
		if self.external_url:
			data += "\nUrl:\n{}\ninstagram.com/{}".format(self.external_url, self.username)
		else:
			data += "\nUrl:\ninstagram.com/{}".format(self.username)
		data = data.replace('https://','').replace('http://','').replace('www.','')
		return data

	def get_avatar(self):
		data = requests.get(SCRAPE_URL.format('profile', self.username))
		data = soup(data.text, 'html.parser')
		data = data.find('a', {'class':'instadp-post'}).find('img').get('src')
		return data

	def get_avatar_wcookie(self, cookie):
		data = requests.get(self.meta_url, headers=cookie).json()['user']
		result = []
		for item in data['hd_profile_pic_versions']:
			result += [{'width': item['width'], 'height': item['height'], 'url': item['url']}]
		item = data['hd_profile_pic_url_info']
		result += [{'width': item['width'], 'height': item['height'], 'url': item['url']}]
		return result

	def get_stories_scraping(self):
		if not self.is_private:

			data = requests.get(SCRAPE_URL.format('stories', self.username), headers=HEADER)
			sleep(0.2)
			data = soup(data.text, 'html.parser')
			data = data.find('ul', {'class':'stories-list'})

			if data:
				data = data.find_all('li', {'class':'story'})
				
			return data

		return False

	def get_stories(self, start=0, stop=101):
		data = self.get_stories_scraping()
		if data:
			data = data[::-1]
			result = []

			for item in data[start:stop]:
				content = item.find('img')
				if not content:
					poster = item.find('video').get('poster')
					content = item.find('source').get('src')
					result += [{'content': content, 'poster': poster, 'type': 'video'}]
					continue
				content = content.get('src')
				result += [{'content': content, 'poster': content, 'type': 'image'}]

			return result

		return None

	def get_posts(self):
		data = self.posts['edges']
		result = []

		for node in data:
			result += ['https://www.instagram.com/p/%s' % node['node']['shortcode']]

		return result

	def get_igtv(self):
		data = self.igtvs['edges']
		result = []

		for node in data:
			result += ['https://www.instagram.com/tv/%s' % node['node']['shortcode']]
			
		return result





