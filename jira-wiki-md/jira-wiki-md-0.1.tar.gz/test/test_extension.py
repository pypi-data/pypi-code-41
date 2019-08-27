import markdown

from jiramd.extension import JiraWikiExtension


def test_monospace():
    text = "foo {{bar}} quz"

    md = markdown.markdown(text, extensions=[JiraWikiExtension()])

    assert md == "<p>foo <pre>bar</pre> quz</p>"

def test_code():
    text = "foo\n{code}\nbar\n{code}"

    md = markdown.markdown(text, extensions=[JiraWikiExtension()])

    assert md == "<p>foo\n<pre><code>\nbar\n</code></pre>\n</p>"
