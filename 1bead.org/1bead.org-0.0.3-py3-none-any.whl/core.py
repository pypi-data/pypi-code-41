from aiohttp import web


INDEX_HTML = """
<html>
<head>
        <title>1bead.org</title>
</head>
<body style="font-size: 120px; text-align: center">
        <h1>Mission</h1>
        Nurture the Greatness of Life
</body>
</html>
"""


async def handle(request):
    return web.Response(text=INDEX_HTML, content_type='text/html')

app = web.Application()
app.add_routes([web.get('/', handle)])
