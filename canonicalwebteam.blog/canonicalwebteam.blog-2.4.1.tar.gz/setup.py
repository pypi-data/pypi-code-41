# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['canonicalwebteam',
 'canonicalwebteam.blog',
 'canonicalwebteam.blog.django',
 'canonicalwebteam.blog.flask']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=1.0,<2.0',
 'canonicalwebteam.http>=1.0.1,<2.0.0',
 'django[django]>=2.2,<3.0',
 'feedgen>=0.7,<0.8']

setup_kwargs = {
    'name': 'canonicalwebteam.blog',
    'version': '2.4.1',
    'description': 'Flask extension and Django App to add a nice blog to your website',
    'long_description': '# Blog flask extension\n\nThis extension allows you to add a simple blog frontend to your flask app. All the articles\nare pulled from the WordPress API that has the plugin WP-JSON.\n\nThis extension provides a blueprint with 3 routes:\n- "/": that returns the list of articles\n- "/<slug>": the article page\n- "/feed": provides a RSS feed for the page.\n## How to use\n\n### Flask\n\nIn your app you can:\n\n```python\n    import canonicalwebteam.blog_extension import BlogExtension\n    blog = BlogExtension(app, "Blog title", [1], "tag_name", "/url-prefix")\n```\nIf you use the factory pattern you can also:\n```python\n    import canonicalwebteam.blog_extension import BlogExtension\n    blog = BlogExtension()\n    blog.init_app(app, "Blog title", [1], "tag_name", "/url-prefix")\n```\n\n### Django\n\n- Add the blog module as a dependency to your Django project\n- Load it at the desired path (f.e. "/blog") in the `urls.py` file\n```python\nfrom django.urls import path, include\nurlpatterns = [path(r"blog/", include("canonicalwebteam.blog.django.urls"))]\n```\n- In your Django project settings (`settings.py`) you have to specify the following parameters:\n```python\nBLOG_CONFIG = {\n    # the id for tags that should be fetched for this blog\n    "TAGS_ID": [3184],\n    # the title of the blog\n    "BLOG_TITLE": "TITLE OF THE BLOG",\n    # the tag name for generating a feed\n    "TAG_NAME": "TAG NAME FOR GENERATING A FEED",\n}\n```\n- Run your project and verify that the blog is displaying at the path you specified (f.e. \'/blog\')\n\n#### Groups pages\n- Group pages are optional and can be enabled by using the view `canonicalwebteam.blog.django.views.group`. The view takes the group slug to fetch data for and a template path to load the correct template from.\n  Group pages can be filtered by category, by adding a `category=CATEGORY_NAME` query parameter to the URL (e.g. `http://localhost:8080/blog/cloud-and-server?category=articles`).\n```python\nfrom canonicalwebteam.blog.django.views import group\n\nurlpatterns = [\n    url(r"blog", include("canonicalwebteam.blog.django.urls")),\n    url(\n        r"blog/cloud-and-server",\n        group,\n        {\n            "slug": "cloud-and-server",\n            "template_path": "blog/cloud-and-server.html"\n        }\n    )\n```\n\n#### Topic pages\n- Topic pages are optional as well and can be enabled by using the view `canonicalwebteam.blog.django.views.topic`. The view takes the topic slug to fetch data for and a template path to load the correct template from.\n\n**urls.py**\n```python\npath(\n\t\tr"blog/topics/kubernetes",\n\t\ttopic,\n\t\t{"slug": "kubernetes", "template_path": "blog/kubernetes.html"},\n\t\tname="topic",\n),\n```\n\n## Templates\n\n- You can now use the data from the blog. To display it the module expects templates at `blog/index.html`, `blog/article.html`, `blog/blog-card.html`, `blog/archives.html`, `blog/upcoming.html` and `blog/author.html`. Inspiration can be found at https://github.com/canonical-websites/jp.ubuntu.com/tree/master/templates/blog.\n\n## Development\nThe blog extension leverages [poetry](https://poetry.eustace.io/) for dependency management.\n\n### Regenerate setup.py\n\n``` bash\npoetry install\npoetry run poetry-setup\n```\n\n## Testing\nAll tests can be run with `poetry run pytest`.\n\n### Regenerating Fixtures\nAll API calls are caught with [VCR](https://vcrpy.readthedocs.io/en/latest/) and saved as fixtures in the `fixtures` directory. If the API updates, all fixtures can easily be updated by just removing the `fixtures` directory and rerunning the tests.\n\nTo do this run `rm -rf fixtures && poetry run pytest`.\n',
    'author': 'Canonical webteam',
    'author_email': 'webteam@canonical.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
