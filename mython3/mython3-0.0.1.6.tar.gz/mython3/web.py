class get:
    def __str__(self):
            return self.text
    def __init__(self, url):
        import urllib.request
        self.url = url
        with open('text.txt', 'wb') as f:
                f.write(urllib.request.urlopen(url).read())
        with open('text.txt', 'rb') as f:
                a = f.read().decode()
                self.text = a
