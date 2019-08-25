import re

def title(html):
    title_reg = re.compile(r"<title.*?>(.*)</title>", re.MULTILINE)
    return title_reg.findall(html)[0]


def find_article(html):
    article_reg = re.compile(r"<article.*?>[\w\W]*?</article>", re.MULTILINE)
    try:
        return article_reg.search(html).group(0)
    except AttributeError:
        return None


def remove_block(text, p):
    return p.sub("", text)


def clean(html, no_scripts):
    # Compile patterns
    head_reg = re.compile(r"<head.*?>([\w\W]*?)<\/head>", re.MULTILINE)
    body_reg = re.compile(r"<body.*?>([\w\W]*?)<\/body>", re.MULTILINE)
    comments_reg = re.compile(r"<!--([\w\W]*?)-->", re.MULTILINE)
    scripts_reg = re.compile(r"<script.*?>([\w\W]*?)<\/script>", re.MULTILINE)
    no_scripts_reg = re.compile(r"(<noscript>|<\/noscript>)", re.MULTILINE)
    nav_reg = re.compile(r"<nav[\w\W]*?>[\w\W]*?</nav>", re.MULTILINE)
    footer_reg = re.compile(r"<footer[\w\W]*?>[\w\W]*?</footer>", re.MULTILINE)
    content = re.compile(
        r"(<((?P<p>p)|(?P<h>h[1-6])).*?>([\w\W]*?)<\/((?P=p)|(?P=h))>)",
        re.MULTILINE
    )

    html = remove_block(html, comments_reg)
    if no_scripts:
        html = remove_block(html, scripts_reg)
        html = remove_block(html, no_scripts_reg)

    head = head_reg.search(html).group(0)
    body = body_reg.search(html).group(0)

    # Find article
    article = find_article(body)

    if article is None:
        body = remove_block(body, nav_reg)
        body = remove_block(body, footer_reg)
        return head, body
        matches = content.findall(body)
        return head, "".join([x[0] for x in matches])
    else:
        return head, f"<body>\n{article}\n</body>"
