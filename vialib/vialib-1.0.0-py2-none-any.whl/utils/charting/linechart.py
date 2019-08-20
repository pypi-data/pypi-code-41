
# The following copyright notice appears due to our use of the aggdraw package and pertains only to the aggdraw package, and to no other code.

#
#    Copyright 1995-2006 by Fredrik Lundh
#
#    By obtaining, using, and/or copying this software and/or its associated documentation, you agree that you have read, understood, and will comply with the following terms and conditions:
#
#    Permission to use, copy, modify, and distribute this software and its associated documentation for any purpose and without fee is hereby granted, provided that the above copyright notice appears in all copies, and that both that copyright notice and this permission notice appear in supporting documentation, and that the name of Secret Labs AB or the author not be used in advertising or publicity pertaining to distribution of the software without specific, written prior permission.
#
#    SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import Image
import aggdraw

import chart_colors

def simple_linechart(values, options={}):
    w = options.get('w') or 300
    h = options.get('h') or 100
    fg_color = options.get('fg_color') or chart_colors.black
    bg_color = options.get('bg_color') or chart_colors.white
    end_caps = options.get('end_caps') or 'DOT'
    end_cap_radius = options.get('end_cap_radius') or 2
    left_margin = options.get('left_margin') or 5
    right_margin = options.get('right_margin') or 5
    top_margin = options.get('top_margin') or 5
    bottom_margin = options.get('bottom_margin') or 5

    img = Image.new('RGB', (w, h), bg_color)
    draw = aggdraw.Draw(img)
    draw.setantialias(True)

    p = aggdraw.Pen(fg_color)
    brush = aggdraw.Brush(fg_color)

    maxv, minv = max(values), min(values)
    
    vrange = h - (top_margin + bottom_margin)
    hrange = w - (right_margin + left_margin)
    
    path = []
    dx = hrange / len(values)
    x = left_margin + dx/2.0
    value_range = maxv - minv

    for v in values:
	dv = v - minv
	if value_range == 0:
		v_pct = .5
	else:
		v_pct = float(dv) / float(value_range)
	y = (vrange - (v_pct * vrange)) + top_margin
	path.extend((x, y))
	x += dx

    draw.line(path, p)

    if end_caps == 'DOT':
	pt = (path[0], path[1])
	bounds = (pt[0] - end_cap_radius, 
		  pt[1] - end_cap_radius, 
		  pt[0] + end_cap_radius,
		  pt[1] + end_cap_radius)
	draw.ellipse(bounds, None, brush)

	pt = (path[-2], path[-1])
	bounds = (pt[0] - end_cap_radius, 
		  pt[1] - end_cap_radius, 
		  pt[0] + end_cap_radius,
		  pt[1] + end_cap_radius)
	draw.ellipse(bounds, None, brush)
	
    draw.flush()
    
    return img
    
def test():
    img = simple_linechart([0, 10, 1, 9, 2, 8, 3, 7, 4, 6, 5, 5, 6, 4, 7, 3, 8, 2, 9, 1, 10, 0])
    img.save('simplelinetest.png')
    return

if __name__ == '__main__':
    test()
