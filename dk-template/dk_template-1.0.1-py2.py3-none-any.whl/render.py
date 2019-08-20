# -*- coding: utf-8 -*-
from dktemplate.parse import nest
from dktemplate.tokenize import tokenize


class Render(object):
    def __init__(self, content):
        self.content = content
        self.out = StringIO()
        self.curlevel = 0

    def value(self):
        return self.out.getvalue()

    def render(self, item=None):
        if item is None:
            item = self.content[0]

        tag = item[0]

        if tag.startswith('block:'):
            tag = 'block'

        #print '[I]', item, 'CALLING:', getattr(self, 'render_' + tag).__name__ , item
        try:
            getattr(self, 'render_' + tag)(item)
        except:
            print '='*80
            print self.out.getvalue()
            raise

    def render_block(self, block):
        print >>self.out, "{%% %s %%}" % block[0]
        if len(block) > 1:
            for item in block[1]:
                self.render(item)
        print >>self.out, "{%% end%s %%}" % block[0]

    def render_tag(self, tag):
        print >>self.out, "{%% %s %%}" % (' '.join(tag[1:]))

    def render_val(self, item):
        print >>self.out, "{{ %s }}" % item[1]


def render(txt):
    r = Render(nest(tokenize(txt)))
    r.render()
    return r.value()
