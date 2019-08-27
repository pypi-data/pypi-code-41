from markdown.extensions import Extension

from jiramd.code import code_processor
from jiramd.monospace import monospace_processor

MONOSPACE_RE = r'(\{\{)(.+?)\}\}'


class JiraWikiExtension(Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(monospace_processor, 'jira-monospace', 200)
        md.inlinePatterns.register(code_processor, 'jira-code', 205)
