"""
Paragraphed Summary
-------
This plugin allows easy, variable length summaries directly embedded into the
body of your articles.
"""

from __future__ import unicode_literals
from bs4 import BeautifulSoup
from pelican import signals
from pelican.generators import ArticlesGenerator, PagesGenerator


def initialized(pelican):
    pass


def extract_summary(instance):
    max_word_count = instance.settings['SUMMARY_MAX_LENGTH']
    soup = BeautifulSoup(instance.content, 'html.parser')
    summary = ''
    word_count = 0
    for child in soup.findAll(recursive=False):
        summary += str(child)
        word_count += count_words(child)
        if word_count >= max_word_count:
            break
    if summary:
        if hasattr(instance, 'default_status'):
            instance.metadata['summary'] = summary
        else:
            instance._summary = summary
        instance.has_summary = True


def count_words(soup):
    rawtext = striptags(soup)
    return len(rawtext.split())


def striptags(soup):
    return ''.join([e for e in soup.recursiveChildGenerator()
                    if isinstance(e, str)])


def run_plugin(generators):
    for generator in generators:
        if isinstance(generator, ArticlesGenerator):
            for article in generator.articles:
                extract_summary(article)
        elif isinstance(generator, PagesGenerator):
            for page in generator.pages:
                extract_summary(page)


def register():
    signals.initialized.connect(initialized)
    try:
        signals.all_generators_finalized.connect(run_plugin)
    except AttributeError:
        # NOTE: This results in #314 so shouldn't really be relied on
        # https://github.com/getpelican/pelican-plugins/issues/314
        signals.content_object_init.connect(extract_summary)
