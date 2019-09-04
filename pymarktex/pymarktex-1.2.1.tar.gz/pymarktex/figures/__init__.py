# Futures #
from __future__ import division

# Built-in modules #

# Internal modules #
from pymarktex import Template

# First party modules #
from autopaths import Path

# Third party modules #

###############################################################################
class LatexFigure(Template):
    def escape_underscore(self, text):
        if text is None: return None
        return text.replace('_', '\\_')

###############################################################################
class ScaledFigure(LatexFigure):
    """A figure in latex code which can have its size adjusted."""

    def __init__(self, path=None, caption=None, label=None, graph=None, **kwargs):
        # Check inputs #
        if path is None and graph is None:
            raise Exception("You need to specify a graph or a path.")
        # Path #
        if path is not None:    self.path = Path(path)
        else:                   self.path = graph.path
        # Caption #
        if caption is not None: self.caption = caption
        else:                   self.caption = ''
        if graph is not None and hasattr(graph, 'caption'): self.caption = graph.caption
        # Label #
        if   label is not None: self.label = r"\label{" + label + "}\n"
        elif graph is not None: self.label = r"\label{" + graph.short_name + "}\n"
        else:                   self.label = ''
        # Graph #
        if graph is not None:   self.graph = graph
        # Keyword arguments #
        self.kwargs  = kwargs
        # Call the graph if it's not generated #
        if graph is not None and not graph: graph()
        # Check the file was created #
        if not self.path.exists: raise Exception("No file at '%s'." % self.path)
        # Check unique extension #
        if self.path.filename.count('.') > 1:
            raise Exception("Can't have several extensions in a LaTeX figure file name.")

    def abs_path(self): return self.path.unix_style

    def graph_params(self):
        params = list('%s=%s' % (k,v) for k,v in self.kwargs.items())
        params += ['keepaspectratio']
        return ','.join(params)

###############################################################################
class DualFigure(LatexFigure):
    """A figure in latex code which has two subfigures."""

    def __init__(self, path_one, path_two, caption_one, caption_two, label_one, label_two, caption_main, label_main):
        # Attributes #
        self.path_one,    self.path_two    = Path(path_one), Path(path_two)
        self.caption_one, self.caption_two = map(self.escape_underscore, (caption_one, caption_two))
        self.caption_main = self.escape_underscore(caption_main)
        self.label_one    = r"\label{" + label_one + "}\n" if label_one is not None else ''
        self.label_two    = r"\label{" + label_two + "}\n" if label_two is not None else ''
        self.label_main   = r"\label{" + label_main + "}\n" if label_main is not None else ''
        # Check #
        if not self.path_one.exists or not self.path_two.exists: raise Exception("File missing.")
        if self.path_one.filename.count('.') > 1 or self.path_two.filename.count('.') > 1:
            raise Exception("Can't have several extension in a LaTeX figure file name.")

    def abs_path_one(self): return self.path_one.unix_style
    def abs_path_two(self): return self.path_two.unix_style
