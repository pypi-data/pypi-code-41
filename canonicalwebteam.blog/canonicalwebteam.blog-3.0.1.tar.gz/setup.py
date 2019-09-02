# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['canonicalwebteam', 'canonicalwebteam.blog', 'canonicalwebteam.blog.django']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=1.0,<2.0',
 'canonicalwebteam.http>=1.0.1,<2.0.0',
 'django[django]>=2.2,<3.0',
 'feedgen>=0.7,<0.8']

setup_kwargs = {
    'name': 'canonicalwebteam.blog',
    'version': '3.0.1',
    'description': 'Flask extension and Django App to add a nice blog to your website',
    'long_description': '# Canonical blog extension\n\nThis extension allows you to add a simple frontend section to your flask app. All the articles\nare pulled from [Canonical\'s Wordpress back-end](https://admin.insights.ubuntu.com/wp-admin/) through the JSON API.\n\nThis extension provides a blueprint with 3 routes:\n\n- "/": that returns the list of articles\n- "/<slug>": the article page\n- "/feed": provides a RSS feed for the page.\n\t\n## How to install\n\nTo install this extension as a requirement in your project, you can use PIP;\n\n```bash\npip install canonicalwebteam.blog\n```\n\nSee also the documentation for (pip install)[https://pip.pypa.io/en/stable/reference/pip_install/].\n\n## How to use\n\n### Templates\n\nThe module expects HTML templates at `blog/index.html`, `blog/article.html`, `blog/blog-card.html`, `blog/archives.html`, `blog/upcoming.html` and `blog/author.html`. \n\nAn example of these templates can be found at https://github.com/canonical-websites/jp.ubuntu.com/tree/master/templates/blog.\n\n### Flask\n\nIn your app you can then:\n\n``` python3\n    import flask\n    from canonicalwebteam.blog import BlogViews\n    from canonicalwebteam.blog.flask import build_blueprint\n\n    app = flask.Flask(__name__)\n\n    # ...\n\n    blog_views = BlogViews()\n    app.register_blueprint(build_blueprint(blog_views), url_prefix="/blog")\n```\n\nYou can customise the blog through the following optional arguments:\n\n``` python3\n    blog_views = BlogViews(\n        blog_title="Blog",\n        tag_ids=[1, 12, 112],\n        exclude_tags=[26, 34],\n    )\n    app.register_blueprint(build_blueprint(blog_views), url_prefix="/blog")\n```\n\n`BlogExtension()` accepts five parameters;\n\n- (obj) `app`\n- (str) "The title of your blog"\n- (arr) Array of tags from blog entries on which to filter e.g `[\'1234\', \'4321\']` \n- (str) Language string e.g. `"lang:en"`\n- (str) "/path/to/display/your/blog"\n\n### Django\n\n- Add the blog module as a dependency to your Django project\n- Load it at the desired path (e.g. "/blog") in the `urls.py` file\n\n```python\nfrom django.urls import path, include\nurlpatterns = [path("blog/", include("canonicalwebteam.blog.django.urls"))]\n```\n\n- In your Django project settings (`settings.py`) you have to specify the following parameters:\n\n```python\nBLOG_CONFIG = {\n    # the id for tags that should be fetched for this blog\n    "TAGS_ID": [3184],\n    # the title of the blog\n    "BLOG_TITLE": "TITLE OF THE BLOG",\n    # the tag name for generating a feed\n    "TAG_NAME": "TAG NAME FOR GENERATING A FEED",\n}\n```\n\n- Run your project and verify that the blog is displaying at the path you specified (e.g. \'/blog\')\n\n#### Groups pages\n\n- Group pages are optional and can be enabled by using the view `canonicalwebteam.blog.django.views.group`. The view takes the group slug to fetch data for and a template path to load the correct template from.\n- Group pages can be filtered by category, by adding a `category=CATEGORY_NAME` query parameter to the URL (e.g. `http://localhost:8080/blog/cloud-and-server?category=articles`).\n  \n```python\nfrom canonicalwebteam.blog.django.views import group\n\nurlpatterns = [\n    url(r"blog", include("canonicalwebteam.blog.django.urls")),\n    url(\n        r"blog/cloud-and-server",\n        group,\n        {\n            "slug": "cloud-and-server",\n            "template_path": "blog/cloud-and-server.html"\n        }\n    )\n```\n\n#### Topic pages\n\n- Topic pages are optional as well and can be enabled by using the view `canonicalwebteam.blog.django.views.topic`. The view takes the topic slug to fetch data for and a template path to load the correct template from.\n\n**urls.py**\n\n```python\npath(\n\t\tr"blog/topics/kubernetes",\n\t\ttopic,\n\t\t{"slug": "kubernetes", "template_path": "blog/kubernetes.html"},\n\t\tname="topic",\n),\n```\n\n## Development\n\nThe blog extension leverages [poetry](https://poetry.eustace.io/) for dependency management.\n\n### Regenerate setup.py\n\n``` bash\npoetry install\npoetry run poetry-setup\n```\n\n## Testing\n\nAll tests can be run with `poetry run pytest`.\n\n### Regenerating Fixtures\n\nAll API calls are caught with [VCR](https://vcrpy.readthedocs.io/en/latest/) and saved as fixtures in the `fixtures` directory. If the API updates, all fixtures can easily be updated by just removing the `fixtures` directory and rerunning the tests.\n\nTo do this run `rm -rf fixtures && poetry run pytest`.\n',
    'author': 'Canonical webteam',
    'author_email': 'webteam@canonical.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
