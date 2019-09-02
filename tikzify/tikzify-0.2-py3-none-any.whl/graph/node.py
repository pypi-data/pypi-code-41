from typing import Any, Mapping, Optional

from ..tikz_generator import pf, pf_option

__all__ = []


def generate_node(name: Optional[str],
                  node_dict: Mapping[str, Any],
                  *,
                  file,
                  end=';\n'):
    fit = None
    if 'fit' in node_dict:
        def get_fits():
            for fit in node_dict['fit']:
                assert isinstance(fit, str)
                yield '(' + fit + ')'
        fit = 'fit={' + " ".join(get_fits()) + '}'

    relpos = pos = None
    if 'pos' in node_dict:
        pos = 'at ({}) '.format(node_dict['pos'].as_tikz())
    if 'relpos' in node_dict:
        x, y, rel_node = node_dict['relpos']
        words = []
        values = []
        if x == 0 and y == 0:
            pos = 'at ({}) '.format(rel_node.as_tikz())
        else:
            if isinstance(y, tuple):
                words.append('above' if y[0] else 'below')
                values.append(y[1])
            elif y > 0:
                words.append('above')
                values.append(y)
            elif y < 0:
                words.append('below')
                values.append(-y)
            if isinstance(x, tuple):
                words.append('right' if x[0] else 'left')
                values.append(x[1])
            elif x > 0:
                words.append('right')
                values.append(x)
            elif x < 0:
                words.append('left')
                values.append(-x)
            relpos = '[{}={} of {}] '.format(
                " ".join(words),
                " and ".join(str(v) for v in values),
                rel_node.as_tikz_ex())
    text = node_dict.get('text', None)
    state = node_dict.get('state', None)
    coordinate = node_dict.get('coordinate', False)
    col = node_dict.get('col', None)
    d = dict(name=name,
             text=text,
             state=state,
             opacity=pf_option(node_dict, 'opacity'),
             inner_sep=pf_option(node_dict, 'inner_sep', 'inner sep'),
             text_width=pf_option(node_dict, 'text_width', 'text width'),
             text_centered=pf_option(node_dict, 'text_centered',
                                     'text centered'),
             col=col,
             dash=node_dict.get('dash', None),
             fit=fit,
             label=pf_option(node_dict, 'label'),
             pos=pos,
             relpos=relpos,
             nodepos=pf_option(node_dict, 'nodepos', 'pos'),
             swap=pf_option(node_dict, 'swap'))
    if coordinate:
        pf(r"""
           \coordinate “relpos” (“name”) “pos”
           """,
           **d,
           file=file,
           end=end)
    else:
        if name is None:
            pf(r"""
               node[“state,opacity,fit,col,dash,inner_sep,label,text_width,text_centered,swap,nodepos”] {“text”}
               """,
               **d,
               file=file,
               end=end)
        else:
            pf(r"""
               \node[“state,opacity,fit,col,dash,inner_sep,label,text_width,text_centered”] “pos”(“name”) “relpos”{“text”}
               """,
               **d,
               file=file,
               end=end)
    if 'corner' in node_dict:
        conditional_dictionary = {}
        if 'opacity' in d:
            conditional_dictionary['opacity'] = d['opacity']
        pf(r"""
           \node[“col,opacity,”align=right, below left] at (“name”.north east) {“text”}
           """,
           name=name,
           col=node_dict['corner'].get('col', col),
           text=node_dict['corner']['text'],
           **conditional_dictionary,
           file=file,
           end=end)
