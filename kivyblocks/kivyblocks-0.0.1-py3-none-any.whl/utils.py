from appPublic.jsonConfig import getConfig


def absurl(url,parent):
	config = getConfig()
	if url.startswith('/'):
		return config.uihome + url
	if url.startswith(config.uihome):
		return url
	if parent == '':
		raise Exception('related url need a parent url')

	if parent.startswith(config.uihome):
		parent = parent[len(config.uihome):]
	paths = parent.split('/')
	paths.pop()
	for i in url.split('/'):
		if i in [ '.', '' ]:
			continue
		if i == '..':
			if len(paths) > 1:
				paths.pop()
			continue
		paths.append(i)
	return config.uihome + '/'.join(paths)

