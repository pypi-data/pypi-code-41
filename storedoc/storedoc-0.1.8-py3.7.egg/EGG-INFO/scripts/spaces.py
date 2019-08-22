from storedoc.s3 import S3Service

class DOService(S3Service):

	def __init__(self, region_name, endpoint_url, **credentials):
		endpoint_url = 'https://{}.digitaloceanspaces.com'.format(region_name)
		super(DOService, self).__init__(region_name, endpoint_url, **credentials)
		self.base_url = endpoint_url
		self.description = 'DigitalOcean Spaces are ideal for storing static, unstructured\
data like audio, video, and images as well as large amounts of text'
		
