from typing import Any, Union

from sanic import Sanic
from sanic import response
from jinja2 import Environment, PackageLoader, select_autoescape, Template

app = Sanic(__name__)

# Load the template environment with async support
template_env = Environment(
    loader=PackageLoader('iapp'),  # 所需文件
    autoescape=select_autoescape(),
    enable_async=True
)

# Load the template from file
template = template_env.get_template("example_template.html")
index_template = template_env.get_template("index.html")
meeting_template = template_env.get_template("meeting.html")


@app.route('/')
async def test(request):
    input = request.args
    output = input.get('v', 'Hello World')

    rendered_template = await template.render_async(knights=output)
    return response.html(rendered_template)



@app.route('/index')
async def index(request):
    _ = await index_template.render_async(body="body")
    return response.html(_)


@app.route('/meeting')
async def meeting(request):
    _ = await meeting_template.render_async(body="body")
    return response.html(_)



app.run(host="0.0.0.0", port=2233, debug=True)
