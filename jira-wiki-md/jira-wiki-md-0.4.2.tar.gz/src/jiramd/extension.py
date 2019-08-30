from markdown.extensions import Extension
from markdown.inlinepatterns import SimpleTagInlineProcessor

from jiramd.code import code_processor
from jiramd.link import link_processor
from jiramd.monospace import monospace_processor

STRONG_RE = r'(?<!\w)(\*)([^\*]+)\1(?!\w)'
EMPHASIS_RE = r'(?<!\w)(_)(.+?)\1(?!\w)'


class JiraWikiExtension(Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(monospace_processor, 'jira-monospace', 200)
        md.inlinePatterns.register(code_processor, 'jira-code', 205)
        md.inlinePatterns.register(link_processor, 'jira-link', 210)
        md.inlinePatterns.register(SimpleTagInlineProcessor(STRONG_RE, 'strong'), 'jira-strong', 199)
        md.inlinePatterns.register(SimpleTagInlineProcessor(EMPHASIS_RE, 'em'), 'jira-emphasis', 198)
        md.inlinePatterns.deregister('strong')
        md.inlinePatterns.deregister('strong2')
        md.inlinePatterns.deregister('emphasis')
        md.inlinePatterns.deregister('emphasis2')
