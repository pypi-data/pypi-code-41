import markdown

from jiramd.extension import JiraWikiExtension


def test_monospace():
    text = "foo {{bar}} quz"

    md = markdown.markdown(text, extensions=[JiraWikiExtension()])

    assert md == "<p>foo <pre>bar</pre> quz</p>"


def test_monospace_with_html():
    text = "foo {{bar<br>}}"

    md = markdown.markdown(text, extensions=[JiraWikiExtension()])

    assert md == "<p>foo <pre>bar&lt;br&gt;</pre>\n</p>"


def test_monospace_with_markdown():
    text = "foo {{*bar*}}"

    md = markdown.markdown(text, extensions=[JiraWikiExtension()])

    assert md == "<p>foo <pre>*bar*</pre>\n</p>"


def test_code():
    text = "foo\n{code}\nbar\n{code}"

    md = markdown.markdown(text, extensions=[JiraWikiExtension()])

    assert md == "<p>foo\n<pre><code>\nbar\n</code></pre>\n</p>"


def test_code_with_html():
    text = "foo\n{code}\nbar<br>\n{code}"

    md = markdown.markdown(text, extensions=[JiraWikiExtension()])

    assert md == "<p>foo\n<pre><code>\nbar&lt;br&gt;\n</code></pre>\n</p>"


def test_code_with_markdown():
    text = "foo\n{code}\n*bar*\n{code}"

    md = markdown.markdown(text, extensions=[JiraWikiExtension()])

    assert md == "<p>foo\n<pre><code>\n*bar*\n</code></pre>\n</p>"
