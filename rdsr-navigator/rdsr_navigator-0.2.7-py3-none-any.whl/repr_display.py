from typing import Sequence

def reper_html(headers: Sequence[str], rows: Sequence[Sequence[object]]) -> str:
    html = [r'<table><thead><tr>', ]

    for header in headers:
        html.append(r'<th>{0}</th>'.format(header))
    html.append(r'</tr></thead><tbody>')

    for row in rows:
        html.append(r'<tr>')
        for value in row:
            html.append(r'<td>{0}</td>'.format(value))
        html.append(r'</tr>')

    html.append(r'</tbody></table>')
    return ''.join(html)
