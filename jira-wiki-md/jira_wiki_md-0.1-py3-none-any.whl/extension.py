from markdown.extensions import Extension
from markdown.inlinepatterns import SimpleTagInlineProcessor

from jiramd.code import code_processor

MONOSPACE_RE = r'(\{\{)(.+?)\}\}'


class JiraWikiExtension(Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(SimpleTagInlineProcessor(MONOSPACE_RE, 'pre'), 'jira-monospace', 200)
        md.inlinePatterns.register(code_processor, 'jira-code', 205)
