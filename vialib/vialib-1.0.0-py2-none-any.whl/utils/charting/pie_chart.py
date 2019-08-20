
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
import math

import chart_colors

C = 360.0

class PieChart:

    # width: width of chart
    # height: height of chart
    # attrcolors: mapping of attribute -> color
    def __init__(self, width, height, attrcolors, sep_attrs=[]):
	self.attrcolors = attrcolors
	self.sep_attrs = sep_attrs
	self.width = width
	self.height = height

    def _drawCanvas(self, attrvalues, w, h):
	canvas_img = Image.new('RGB', (w, h), chart_colors.white)
	bb = (7, 7, w-7, h-7)

	sum = 0.0
	for attr in attrvalues:
	    value = attrvalues[attr]
	    sum += float(value)
	if sum == 0.0:
	    return canvas_img

	draw = aggdraw.Draw(canvas_img)
	draw.setantialias(True)

	if not self.sep_attrs:
	    last_angle = 0
	    for attr in attrvalues:
		value = float(attrvalues[attr])
		proportion = value / sum
		angle = last_angle + (proportion * C)
		b = aggdraw.Brush(self.attrcolors.get(attr))
		draw.pieslice(bb, last_angle, angle, None, b)
		last_angle = angle
	else:
	    remaining_attrs = filter(lambda x: x not in self.sep_attrs, attrvalues.keys())
	    first_angle = 0
	    last_angle = 0
	    for attr in self.sep_attrs:
		value = attrvalues.get(attr)
		if value is None: continue
		value = float(value)
		proportion = value / sum
		angle = last_angle + (proportion * C)
		b = aggdraw.Brush(self.attrcolors.get(attr))
		draw.pieslice(bb, last_angle, angle, None, b)
		last_angle = angle

	    p = aggdraw.Pen(chart_colors.sep_pie_color, width=3)
	    draw.pieslice(bb, first_angle, angle, p)
	    
	    remaining_deg = angle + ((360 - angle) / 2)
	    remaining_rad = math.radians(remaining_deg)
	    dx = 6.0 * math.cos(remaining_rad)
	    dy = -6.0 * math.sin(remaining_rad)
	    bb = ( bb[0] + dx,
		   bb[1] + dy,
		   bb[2] + dx, 
		   bb[3] + dy )

	    last_angle = angle
	    for attr in remaining_attrs:
		value = attrvalues.get(attr)
		if value is None: continue
		value = float(value)
		proportion = value / sum
		angle = last_angle + (proportion * C)
		b = aggdraw.Brush(self.attrcolors.get(attr))
		draw.pieslice(bb, last_angle, angle, None, b)
		last_angle = angle

	draw.flush()
	return canvas_img
	

    # attrvalues: mapping of attribute -> value
    def getChart(self, attrvalues):
	chart_img = Image.new('RGB', 
			      (self.width, self.height), 
			      chart_colors.white)
	canvas_img = self._drawCanvas(attrvalues, self.width, self.height)
	chart_img.paste(canvas_img, None)

	return chart_img

def test1(name='pietest.png'):
    attrcolors = { 'Software Engineers': chart_colors.red,
		   'Human Scientists': chart_colors.green,
		   'Visual Designers': chart_colors.blue }
    values = { 'Software Engineers': 12,
	       'Human Scientists': 5,
	       'Visual Designers': 4 }
    pie = PieChart(300, 300, attrcolors)
    img = pie.getChart(values)
    img.save(name)
    return

def test2(name='pietest.png'):
    attrcolors = { 'Software Engineers': chart_colors.boy_teal,
		   'Human Scientists': chart_colors.mustard,
		   'Visual Designers': chart_colors.light_green,
		   'Civilians': chart_colors.tan }
    sep_attrs = [ 'Software Engineers',
		  'Human Scientists',
		  'Visual Designers' ]
    values = { 'Software Engineers': 12,
	       'Human Scientists': 5,
	       'Visual Designers': 4,
	       'Civilians': 10 }
    pie = PieChart(300, 300, attrcolors, sep_attrs=sep_attrs)
    img = pie.getChart(values)
    img.save(name)
    return

def test3(name='pietest.png'):
    attrcolors = { 'Software Engineers': chart_colors.boy_teal,
		   'Human Scientists': chart_colors.mustard,
		   'Visual Designers': chart_colors.light_green,
		   'Civilians': chart_colors.tan }
    sep_attrs = [ 'Civilians' ]
    values = { 'Software Engineers': 12,
	       'Human Scientists': 5,
	       'Visual Designers': 4,
	       'Civilians': 10 }
    pie = PieChart(300, 300, attrcolors, sep_attrs=sep_attrs)
    img = pie.getChart(values)
    img.save(name)
    return

if __name__ == '__main__':
    test2()
