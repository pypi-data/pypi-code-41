import html
import re

def remove_tags(raw_html):
    cleaner = re.compile('<.*?>')
    clean_text = re.sub(cleaner, '', raw_html)
    return html.unescape(clean_text)
