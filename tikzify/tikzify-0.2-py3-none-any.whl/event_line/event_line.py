from typing import TextIO

import numpy as np

from ..tikz_generator import pf

__all__ = ['EVENT_LINE_WIDTH',
           'FILL_OPACITY',
           'MARK_HEIGHT',
           'MARK_WIDTH',
           'draw_curve',
           'event_line',
           'event_line_marks']

# Event drawing constants
EVENT_LINE_WIDTH = 8.5
EVENT_LINE_EXTRA = 0.2
FILL_OPACITY = 0.4
MARK_WIDTH = 0.06
MARK_HEIGHT = 0.3


def event_line_mark(f: TextIO, x, y, col, scale=1.0):
    h = scale * MARK_HEIGHT * 0.5
    w = scale * MARK_WIDTH
    pf(r"""
       \draw[“col”, -, ultra thick] (“x”, “top”) -- (“x”, “bottom”);
       """,
       col=col,
       x=x,
       xl=x - w,
       xr=x + w,
       top=y + h,
       bottom=y - h,
       file=f)


def event_line_marks(f: TextIO, y, marks, mark_color=None):
    for x in marks:
        event_line_mark(f, x * EVENT_LINE_WIDTH, y, mark_color)


def event_line(f: TextIO, name, y, left=0, right=1, arrow=False):
    pf(r"""
       \node [left] at (“left”, “y”) {“name”};
       \path (“left”, “y”) edge [“arrow”] (“right”, “y”);
       """,
       name=name,
       arrow='->' if arrow else '-',
       y=y,
       left=left * EVENT_LINE_WIDTH,
       right=right * EVENT_LINE_WIDTH + (EVENT_LINE_EXTRA if arrow else 0.0),
       file=f)


def draw_curve(f: TextIO,
               color,
               fill_color,
               curve_elements,
               fill,
               transform=(lambda x, y: (x, y)),
               options=None,
               clip=(-10.0, 10.0)):
    pf(r"""\“drawcmd” [-, thin, draw=“color”“,fill,options”]
       plot coordinates {
       """,
       options=options,
       drawcmd='filldraw' if fill else 'draw',
       fill=(r"“fill_color”, fill opacity=“fill_opacity”" if fill else ""),
       fill_opacity=FILL_OPACITY,
       color=color,
       fill_color=fill_color,
       end=' ',
       file=f)

    for curve_element in curve_elements:
        for time, value in curve_element.draw_points(fill):
            time, value = transform(time, value)
            if np.isnan(value):
                value = clip[0]
            else:
                value = np.clip(value, *clip)
            pf(r'(“x:.6f”, “y:.6f”)',
               x=time,
               y=value,
               end=' ',
               file=f)

    pf('};', file=f)
