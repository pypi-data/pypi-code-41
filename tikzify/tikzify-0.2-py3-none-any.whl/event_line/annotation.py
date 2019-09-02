from typing import Sequence, TextIO

from ..graph.edge import Edge
from ..tikz_generator import pf, pf_option_value
from .event_line import EVENT_LINE_WIDTH, MARK_HEIGHT, MARK_WIDTH

__all__ = ['RectAnnotation', 'BraceAnnotation', 'CircleAnnotation',
           'EdgeAnnotation']

# Annotation
BRACE_HEIGHT = 0.3
UNCIRCLED_HEIGHT = 0.15
CIRCLE_HEIGHT = 0.25  # Offset of annotation.
CIRCLE_SCALE = 0.7  # corresponds to tikz_flow.tex
ARROW_SPACING = 0.40
SWIPE_OFFSET = -0.6
SWIPE_ANGLE = 50
LOOP_LOOSENESS = 1.5


class RectAnnotation:

    def __init__(self,
                 left,
                 right,
                 top,
                 bottom,
                 text='*',
                 direction='above',
                 coordinate='top',
                 text_size=r'\footnotesize',
                 widen=True):
        self.text_size = text_size
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.widen = widen
        self.text = text
        self.direction = direction
        self.coordinate = coordinate

    def generate(self, f: TextIO):
        left = self.left * EVENT_LINE_WIDTH - MARK_WIDTH * self.widen
        right = self.right * EVENT_LINE_WIDTH + MARK_WIDTH * self.widen
        top = self.top + BRACE_HEIGHT
        bottom = self.bottom - BRACE_HEIGHT
        pf(r"""
           \coordinate (ll) at (“left”, “bottom”);
           \coordinate (ur) at (“right”, “top”);
           \node [shape=rectangle, thin, draw=ann_col, fill=h_ann_col, fill opacity=0.4, fit={(ll) (ur)}] (A) {};
           \node [ann_col, “direction”=0mm of A.“coordinate”] {“text_size” “text”};
           """,
           coordinate=self.coordinate,
           top=top,
           left=left,
           right=right,
           bottom=bottom,
           direction=self.direction,
           text_size=self.text_size,
           text=self.text,
           file=f)


class BraceAnnotation:

    def __init__(self,
                 left: float,
                 right: float,
                 y: float,
                 *,
                 text='*',
                 direction='above',
                 text_size=r'\footnotesize',
                 widen=True):
        self.text_size = text_size
        self.left = left
        self.right = right
        self.y = y
        self.widen = widen
        self.text = text
        self.direction = direction

    def generate(self, f: TextIO):
        left = self.left * EVENT_LINE_WIDTH - MARK_WIDTH * self.widen
        right = self.right * EVENT_LINE_WIDTH + MARK_WIDTH * self.widen
        amp = (right - left) * 1.0
        pf(r"""
           \draw [-, decoration={brace,amplitude=“amp”mm}, decorate, thick, “color”] (“left”, “y”) -- (“right”, “y”)
           node [midway, inner sep=1pt, “color”,
           “direction”=“ampx”mm] {“text_size” “text”};
           """,
           amp=amp,
           ampx=amp + 0.5,
           left=left,
           right=right,
           y=self.y + BRACE_HEIGHT,
           color='ann_col',
           direction=self.direction,
           text=self.text,
           text_size=self.text_size,
           file=f)


class CircleAnnotation:

    def __init__(self,
                 x: float,
                 y: float,
                 text='*',
                 direction='above',
                 draw_circle=True,
                 color='ann_col'):
        self.x = x
        self.y = y
        self.text = text
        self.direction = direction
        self.draw_circle = draw_circle
        self.color = color

    def generate(self, f: TextIO):
        pf(r"""
           \node[shape=circle, “draw,” inner sep=1pt, “color,”
           “direction”=“circle_height”]
           at (“x”, “y”) {\footnotesize “text”};
           """,
           direction=self.direction,
           draw='draw' if self.draw_circle else None,
           circle_height=(CIRCLE_HEIGHT
                          if self.draw_circle
                          else UNCIRCLED_HEIGHT),
           color=self.color,
           x=self.x * EVENT_LINE_WIDTH,
           y=self.y,
           text=self.text,
           file=f)


class EdgeAnnotation:

    def __init__(self,
                 y_source: float,
                 y_targets: Sequence[float],
                 x_source,
                 edge_colors,
                 *,
                 x_target=None,
                 swipe=None,
                 # edge options
                 from_=None,
                 to=None,
                 bend=0,
                 in_=None,
                 out=None,
                 looseness=None,
                 loop=None,
                 opacity=1,
                 dash=None,
                 swipe_right=False,
                 # edge label options
                 text='*',
                 swap=False,
                 pos=None):
        self.swipe = swipe
        self.y_source = y_source
        self.y_targets = y_targets
        self.x_source = x_source
        self.x_target = (x_source
                         if x_target is None
                         else x_target)
        self.text = text
        self.swap = swap
        self.pos = pos
        self.loop = loop
        self.edge = Edge(edge_colors=edge_colors,
                         from_=from_,
                         to=to,
                         bend=bend,
                         in_=in_,
                         out=out,
                         looseness=looseness,
                         opacity=opacity,
                         dash=dash)
        self.swipe_right = swipe_right

    def generate(self, f):
        x_source = self.x_source
        x_target = self.x_target

        def reverse_angle(angle, do_it):
            return 180 - angle if do_it else angle

        def create_node(name, x, y, space):
            if space:
                pf(r"\node (“name”) at (“x”, “y”) "
                   + r"[shape=rectangle, minimum width=“width”cm, "
                   + r"minimum height=“height”cm] {};",
                   name=name,
                   width=MARK_WIDTH,
                   height=MARK_HEIGHT,
                   x=x * EVENT_LINE_WIDTH,
                   y=y,
                   file=f)
            else:
                pf(r"\coordinate (“name”) at (“x”, “y”);",
                   name=name,
                   x=x * EVENT_LINE_WIDTH,
                   y=y,
                   file=f)
        y_source = self.y_source
        y_targets = sorted(self.y_targets)
        swap = self.swap
        swipe = len(y_targets) > 1 or self.swipe or self.loop

        # text
        if swipe:
            below = y_targets and y_source > y_targets[0]
            if below:
                y_targets.reverse()
                direction = -1
            else:
                swap = not swap
                direction = 1

        text_node = (dict(col=self.edge.color(),
                          pos=pf_option_value('pos', self.pos),
                          swap='swap' if swap else None,
                          text=self.text)
                     if self.text is not None
                     else None)

        # create source node
        create_node('source node', x_source, y_source, True)

        # create target nodes
        for i, y_target in enumerate(y_targets):
            create_node(f'node {i}', x_target, y_target, True)

        # create swipe nodes
        if swipe:
            self.edge.col = self.edge.color()
            dy = 0.7
            x = (min(x_source, x_target)
                 + (-1.0 if self.swipe_right else 1.0)
                 * SWIPE_OFFSET / EVENT_LINE_WIDTH)
            create_node('swipe node source', x, y_source + direction * dy,
                        False)
            for i, y in enumerate(y_targets):
                create_node(f'swipe node {i}', x, y - direction * dy,
                            False)

            self.edge.out = reverse_angle((90 + SWIPE_ANGLE) * direction,
                                          self.swipe_right)
            self.edge.in_ = reverse_angle(-90 * direction,
                                          self.swipe_right)
            to, self.edge.to = self.edge.to, None
            self.edge.pf(f, 'source node', 'swipe node source',
                         text_node=text_node)

            self.edge.out = reverse_angle(90 * direction,
                                          self.swipe_right)
            from_, self.edge.from_ = self.edge.from_, None
            if y_targets:
                self.edge.pf(f, 'swipe node source',
                             'swipe node {}'.format(len(y_targets) - 1))

            self.edge.in_ = reverse_angle(-(90 + SWIPE_ANGLE) * direction,
                                          self.swipe_right)
            self.edge.from_ = from_
            self.edge.to = to
            for i, y_target in enumerate(y_targets):
                self.edge.pf(f,
                             f'swipe node {i}',
                             f'node {i}')

            if self.loop:
                self.edge.out = (90) * direction
                self.edge.in_ = (90) * direction
                self.edge.looseness = LOOP_LOOSENESS
                self.edge.pf(f, 'swipe node source', 'source node')
        else:
            self.edge.pf(f,
                         'source node',
                         f'node 0',
                         text_node=text_node)
