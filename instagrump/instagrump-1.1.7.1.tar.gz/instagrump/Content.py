import requests
from time import sleep


API_ENDP = '__a=1'

class Content:
	
	def __init__(self, url):

		if not API_ENDP in url:
			if '?' in url:
				url += '&%s' % API_ENDP
			else:
				url += '?%s' % API_ENDP

		self.data = requests.get(url)
		sleep(0.4)
		self.data = self.data.json()['graphql']['shortcode_media']
		self.type = self.data['__typename']
		self.id = self.data['id']
		self.caption = self.data['edge_media_to_caption']['edges']
		self.captions = [item['node']['text'] for item in self.caption]
		self.caption_is_edited = self.data['caption_is_edited']
		self.tagged_user = self.data['edge_media_to_tagged_user']['edges']
		self.username = self.data['owner']['username']
		self.is_video = self.data['is_video']
		self.dimensions = self.data['dimensions']
		self.location = self.data['location']
		self.timestamp = self.data['taken_at_timestamp']
		self.likes = self.data['edge_media_preview_like']['count']
		self.comments_disabled = self.data['comments_disabled']
		self.viewer_can_reshare = self.data['viewer_can_reshare']
		self.has_ranked_comments = self.data['has_ranked_comments']

		try:
			self.comments = self.data['edge_media_to_parent_comment']
			self.comments_length = self.comments['count']
		except:
			self.comments = None
			self.comments_length = None
		
	def __len__(self):
		data = self.get_content()
		return len(data)

	def __str__(self):
		data = "{}\n".format(self.username)
		data += "Likes: {:,}\n".format(self.likes)
		if self.comments_length:
			data += "Comments: {:,}\n".format(self.comments_length)
		data += "Length: {:,}\n".format(self.__len__())
		data += "\nCaption:"
		if not self.captions:
			data += '\n--'

		for item in self.captions:
			data += '\n'+item+'\n'

		return data[:-1][:1990]

	def get_content(self):
		if self.type == 'GraphSidecar':
			data = self.data['edge_sidecar_to_children']['edges']
		else:
			data = [{'node':self.data}]

		result = []
		for node in data:
			item = {}
			if node['node']['is_video']:
				item['content'] = node['node']['video_url']
				item['type'] = 'video'
			else:
				item['content'] = node['node']['display_url']
				item['type'] = 'image'
			item['poster'] = node['node']['display_url']
			result += [item]

		return result




