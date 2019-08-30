import markdown

from jiramd.extension import JiraWikiExtension


def test_monospace():
    text = "foo {{bar}} quz"

    md = markdown.markdown(text, extensions=[JiraWikiExtension()])

    assert md == "<p>foo <code>bar</code> quz</p>"


def test_monospace_with_html():
    text = "foo {{bar<br>}}"

    md = markdown.markdown(text, extensions=[JiraWikiExtension()])

    assert md == "<p>foo <code>bar&lt;br&gt;</code></p>"


def test_monospace_with_markdown():
    text = "foo {{*bar*}}"

    md = markdown.markdown(text, extensions=[JiraWikiExtension()])

    assert md == "<p>foo <code>*bar*</code></p>"


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


def test_jira_strong():
    text = '*foo*'

    md = markdown.markdown(text, extensions=[JiraWikiExtension()])

    assert md == '<p><strong>foo</strong></p>'


def test_jira_emphasis():
    text = '_foo_'

    md = markdown.markdown(text, extensions=[JiraWikiExtension()])

    assert md == '<p><em>foo</em></p>'


def test_jira_emphasis_unspaced():
    text = 'this_foo_bar'

    md = markdown.markdown(text, extensions=[JiraWikiExtension()])

    assert md == '<p>this_foo_bar</p>'


def test_jira_emphasis_end_sentence():
    text = 'this is _foo_.'

    md = markdown.markdown(text, extensions=[JiraWikiExtension()])

    assert md == '<p>this is <em>foo</em>.</p>'


def test_link():
    text = '[foo|https://test.org/]'

    md = markdown.markdown(text, extensions=[JiraWikiExtension()])

    assert md == '<p><a href="https://test.org/">foo</a></p>'
