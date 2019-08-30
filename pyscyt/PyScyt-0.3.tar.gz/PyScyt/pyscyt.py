import json
from functools import wraps


class PyScyt:
    def __init__(self, project_name):
        self.project_name = project_name
        self.project_json = {}

    def medium_article(self, f):
        @wraps(f)
        def decorator(*args, **kwargs):
            post = f(*args, **kwargs)
            post['edit_link'] = 'https://medium.com/p/{}/edit'.format(post['id'])
            self.project_json['medium_article'] = post
            return post
        return decorator

    def run(self):
        self.project_json = {self.project_name: self.project_json}
        with open('%s.json' % self.project_name, 'w') as f:
            json.dump(self.project_json, f, indent=4, sort_keys=True)
        return self.project_json
