
import Image, ImageDraw, ImageFont
import math

import chart_colors

import inspect
import sys
import os


# return black for each value in v
def default_coloring(v):
    return map(lambda x: chart_colors.black, v)

def execution_path(filename):
      return os.path.join(os.path.dirname(inspect.getfile(sys._getframe(1))), filename)

class BarChart:

    label_gutter = 6
    #font = ImageFont.load("fonts/courB08.pil")
    RELATIVE_PATH = "fonts/ARIAL.TTF"
    yfont = ImageFont.truetype(execution_path(RELATIVE_PATH), 10)
    xfont = ImageFont.truetype(execution_path(RELATIVE_PATH), 12)


    def __init__(self,
		 width, # width of chart
		 height, # height of chart
		 measures, # list of (label, value) for delineating dep axis
		 barcolors=None, # function mapping values to colors
		 bar_width=5, # width of bars
		 top_axis=False, # draw a dependent axis on the top
		 grow_left=False, # bars grow to the left, not right
		 jam=False, # jam clumps together
		 ):
	if barcolors is None:
	    barcolors = default_coloring
	self.barcolors = barcolors
	self.bar_width = bar_width
	self.measures = measures
	self.width = width
	self.height = height
	self.top_axis = top_axis
	self.grow_left = grow_left
	self.jam = jam

	self.attrs = []

    def getMinMax(self, values):
	all_values = self.getMeasureValues() + self.getValues(values)
	return (min(all_values), max(all_values))

    def drawDottedSeparator(self, draw, xy, length):
	(x, y) = xy
	ey = y + length
	while y < ey:
	    draw.point((x, y), fill=chart_colors.dot_color)
	    y += 2
	return

    def drawDashedSeparator(self, draw, xy, length):
	(x, y) = xy
	ex = x + length
	while x < ex:
	    draw.point((x, y), fill=chart_colors.dot_color)
	    draw.point((x+1, y), fill=chart_colors.dot_color)
	    draw.point((x+2, y), fill=chart_colors.dot_color)
	    x += 5
	return

    def getMeasureLabels(self):
	return map(lambda x: x[0], self.measures)
    
    def getMeasureValues(self):
	return map(lambda x: x[1], self.measures)

    def getMeasurePosition(self, x, w, m, values):
	(min, max) = self.getMinMax(values)
	if self.grow_left:
	    return x + (w - ((float(m)/ max) * w))
	else:
	    return x + ((float(m)/ max) * w)

    def getClumpPosition(self, h, attr, values):
	jam = self.jam
	n_clumps = len(self.attrs)
	all_values = self.getValues(values)
	n_values = len(all_values)
	total_bar_width = n_values * self.bar_width 
	leftover_space = h - total_bar_width
	if jam:
	    spacing = leftover_space
	else:
	    spacing = leftover_space / n_clumps

	y = spacing / 2
	for a in self.attrs:
	    vs = values[a]
	    w = self.bar_width * len(vs)
	    if a == attr:
		return (y, y+w)
	    if jam:
		y += w
	    else:
		y += (w + spacing)

	raise ValueError("No such attribute! " + str(attr))

    def getValues(self, values):
	flat = []
	for attr in self.attrs:
	    vs = values[attr]
	    flat.extend(vs)
	return flat

    def getValueDict(self, values):
	nv = {}
	for (attr, vs) in values:
	    nv[attr] = vs
	return nv

    def processValues(self, values):
	self.attrs = []
	nv = {}
	for (attr, vs) in values:
	    self.attrs.append(attr)
	    nv[attr] = vs
	return nv

    def getCanvas(self, values, w, h, line_values=None):
	jam = self.jam
	canvas_img = Image.new('RGB', (w, h), chart_colors.white)
	draw = ImageDraw.Draw(canvas_img)
	
	(label_maxw, label_maxh) = self.getMaxLabelSizes(draw, self.getMeasureLabels(), self.xfont)

	n_clumps = len(self.attrs)
	n_values = len(self.getValues(values))
	bar_width = self.bar_width
	all_bar_width = bar_width * n_values
	if jam:
	    clump_spacing = (h-all_bar_width)
	else:
	    clump_spacing = (h-all_bar_width) / n_clumps

	(min, max) = self.getMinMax(values)
	if line_values:
	    line_values = self.getValueDict(line_values)
	    (min_lv, max_lv) = self.getMinMax(line_values)
	    if min_lv < min:
		min = min_lv
	    if max_lv > max:
		max = max_lv
	local_w = w - label_maxw - self.label_gutter

	x = 0
	y = 0
	for m in self.getMeasureValues():
	    if self.grow_left:
		x = self.getMeasurePosition(label_maxw + self.label_gutter, 
					    local_w, m, values)
	    else:
		x = self.getMeasurePosition(0, local_w, m, values)
	    self.drawDottedSeparator(draw, (x, y), h)

	x = 0
	y = clump_spacing / 2
	i = 0
	for attr in self.attrs:
	    i += 1
	    vs = values[attr]
	    colors = self.barcolors(vs)
	    for (v, c) in zip(vs, colors):
		bar_length = (float(v) / max) * local_w
		bar_w  = bar_width
		if self.grow_left:
                    if v:
  		        draw.rectangle((w, y, w-bar_length, y+bar_w),
			  	       fill=c)
		else:
                    if v: 
		        draw.rectangle((x, y, int(x+bar_length), y+bar_w), 
				       fill=c)
		      
		y += bar_w
	    if not jam:
		y += clump_spacing
	    elif i != len(self.attrs):
		self.drawDashedSeparator(draw, (x, y), w)

	if line_values:
	    line_pts = []

	    x = 0
	    y = clump_spacing / 2
	    i = 0
	    for attr in self.attrs:
		i += 1
		vs = line_values[attr]
		for v in vs:
		    pt_x = (float(v) / max) * local_w
		    bar_w  = bar_width
		    if self.grow_left:
			line_pts.append(w - pt_x)			
		    else:
			line_pts.append(x + pt_x)
		    line_pts.append(y + (bar_w/2.0))
		    y += bar_w
		if not jam:
		    y += clump_spacing
	    draw.line(line_pts, fill=0)

	return canvas_img
		  
    def getDependentAxis(self, w, h, xoffset, values, top=False):
	dep_axis_img = Image.new('RGB', (w, h), chart_colors.white)	
	draw = ImageDraw.Draw(dep_axis_img)

	(label_maxw, label_maxh) = self.getMaxLabelSizes(draw, self.getMeasureLabels(), self.xfont)

	y = self.label_gutter
	local_w = w - xoffset - self.label_gutter - label_maxw
	for (label, m) in self.measures:
	    if self.grow_left:
		x = self.getMeasurePosition(self.label_gutter + label_maxw, local_w, m, values)
	    else:
		x = self.getMeasurePosition(xoffset, local_w, m, values)
	    (lw, lh) = draw.textsize(label, font=self.xfont)
	    x -= (lw/2)
	    draw.text((x, y), label, font=self.xfont, fill=chart_colors.gray_75)

	if top:
	    y = (self.label_gutter * 2) + label_maxh
	else:
	    y = 0
	if self.grow_left:
	    draw.line((0, y, w-1-xoffset, y), fill=chart_colors.axis_color)
	else:
	    draw.line((xoffset, y, w-1, y), fill=chart_colors.axis_color)
	
	return dep_axis_img

    def getIndependentAxis(self, values, w, h):
	ind_axis_img = Image.new('RGB', (w, h), chart_colors.white)
	draw = ImageDraw.Draw(ind_axis_img)
	
	labels = self.attrs
	for label in labels:
	    (sy, ey) = self.getClumpPosition(h, label, values)
	    y = (sy+ey)/2
	    (lw, lh) = draw.textsize(label, font=self.yfont)
	    y -= (lh/2)
	    if self.grow_left:
		x = self.label_gutter
	    else:
		x = w - lw - self.label_gutter
	    draw.text((x, y), label, font=self.yfont, fill=chart_colors.black)

	if self.grow_left:
	    draw.line((0, 0, 0, h-1), fill=chart_colors.axis_color)
	else:
	    draw.line((w-1, 0, w-1, h-1), fill=chart_colors.axis_color)

	return ind_axis_img

    def getMaxLabelSizes(self, draw, labels, font):
	label_sizes = map(lambda x: draw.textsize(x, font=font),
			  labels)
	label_widths = map(lambda x: x[0], label_sizes)
	label_heights = map(lambda x: x[1], label_sizes)
	return (max(label_widths), max(label_heights))

    # returns Image object
    # values is a sequence of (ind axis variable name, sequence of values)
    # the order of the values should be consistent
    def getChart(self, values):
	values = self.processValues(values)

	chart_img = Image.new('RGB',
			      (self.width, self.height),
			      chart_colors.white)
	draw = ImageDraw.Draw(chart_img)

	(label_maxw, label_maxh) = self.getMaxLabelSizes(draw, self.attrs, self.yfont)
	(measure_label_maxw, measure_label_maxh) = self.getMaxLabelSizes(draw, self.getMeasureLabels(), self.xfont)
	n_measures = len(self.getMeasureLabels())

	ind_axis_w = label_maxw + (self.label_gutter * 2) + 1
	dep_axis_w = self.width 
	dep_axis_xoffset = ind_axis_w
	dep_axis_h = measure_label_maxh + (self.label_gutter * 2) + 1
	if self.top_axis:
	    ind_axis_h = self.height - (dep_axis_h*2)
	else:
	    ind_axis_h = self.height - dep_axis_h	

	ind_axis_img = self.getIndependentAxis(values,
					       ind_axis_w,
					       ind_axis_h)
	
	dep_axis_img = self.getDependentAxis(dep_axis_w, dep_axis_h, 
					     dep_axis_xoffset, values)
	if self.top_axis:
	    top_dep_axis_img = self.getDependentAxis(dep_axis_w,
						     dep_axis_h,
						     dep_axis_xoffset,
						     values,
						     top=True)

	canvas_w = self.width - ind_axis_w 
	if self.top_axis:
	    canvas_h = self.height - (dep_axis_h*2)
	else:
	    canvas_h = self.height - dep_axis_h
	
	canvas_img = self.getCanvas(values, canvas_w, canvas_h)
	
	if self.grow_left:
	    if self.top_axis:
		chart_img.paste(ind_axis_img, (canvas_w, dep_axis_h))
		chart_img.paste(top_dep_axis_img, (0, 0))
		chart_img.paste(dep_axis_img, (0, ind_axis_h + dep_axis_h))
		chart_img.paste(canvas_img, (0, dep_axis_h))
	    else:
		chart_img.paste(ind_axis_img, (canvas_w, 0))
		chart_img.paste(dep_axis_img, (0, ind_axis_h))
		chart_img.paste(canvas_img, (0, 0))
	else:
	    if self.top_axis:
		chart_img.paste(ind_axis_img, (0, dep_axis_h))
		chart_img.paste(top_dep_axis_img, (0, 0))
		chart_img.paste(dep_axis_img, (0, ind_axis_h + dep_axis_h))
		chart_img.paste(canvas_img, (ind_axis_w, dep_axis_h))
	    else:
		chart_img.paste(ind_axis_img, (0, 0))
		chart_img.paste(dep_axis_img, (0, ind_axis_h))
		chart_img.paste(canvas_img, (ind_axis_w, 0))

	return chart_img

# simple bar chart with only one value per attribute
# demonstrates distinct measure labels and constant color selection
def test1(name='bartest.png'):
    w = 397
    h = 174
    measures = ( ('0.0%', 0.0), ('1.0%', 0.01), ('2.0%', 0.02), 
		 ('3.0%', 0.03), ('4.0%', 0.04), ('5.0%', 0.05) )
    def color_mapping(vs):
	return map(lambda x: chart_colors.tan, vs)
    charter = BarChart(w, h, measures, barcolors=color_mapping)
    
    values = ( ('Graduate', (.019,)), 
	       ('Undergraduate', (0.019,)),
	       ('Grade 9-12', (0.048,)), 
	       ('Grade 5-8', (0.048,)),
	       ('Grade 1-4', (0.048,)), 
	       ('Kindergarten', (0.046,)), 
	       ('Preschool', (.019,)) )
    img = charter.getChart(values)
    img.save(name)
    return

# multiple values per attribute
# positional color selection
def test2(name='bartest.png'):
    w = 406
    h = 182
    measures = map(lambda x: (str(x), x), [0, 20, 40, 60, 80, 100])
    def color_mapping(vs):
	return (chart_colors.boy_teal, chart_colors.girl_orange)
    charter = BarChart(w, h, measures, barcolors=color_mapping)

    values = ( ('Graduate Degree', (40, 18)), 
	       ("Bachelor's Degree", (38, 22)), 
	       ('Associate Degree', (98, 45)),
	       ('Some College', (56, 20)), 
	       ('High School Diploma', (30, 24)), 
	       ('Grade 9-12', (80, 23)),
	       ('< Grade 9', (41, 14)) )
    img = charter.getChart(values)
    img.save(name)
    return

# single value per attribute
# distinct measure labels
# top and bottom dependent axes
# value based color mapping
# XXX exhibits some extra space at the bottom due to rounding errors
def test3(name='bartest.png'):
    w = 383
    h = 420
    measures = ( ('0', 0), ('10,000', 10000), ('20,000', 20000),
		 ('30,000', 30000), ('40,000', 40000), ('50,000', 50000) )
    def color_mapping(vs):
	cs = []
	for v in vs:
	    if v > 40000:
		cs.append(chart_colors.girl_pink)
	    elif v > 20000:
		cs.append(chart_colors.light_green)
	    else:
		cs.append(chart_colors.boy_teal)
	return cs
    charter = BarChart(w, h, measures, barcolors=color_mapping, top_axis=True)
    values = ( ("<$10K", (3000,)),
	       ("$10K - $14,999", (5000,)),
	       ("$15K - $19,999", (8000,)),
	       ("$20K - $24,999", (9000,)),
	       ("$25K - $29,999", (10500,)),
	       ("$30K - $34,999", (12000,)),
	       ("$35K - $39,999", (15000,)),
	       ("$40K - $49,999", (29000,)),
	       ("$50K - $59,999", (35000,)),
	       ("$60K - $69,999", (41500,)),
	       ("$70K - $79,999", (39500,)),
	       ("$80K - $89,999", (41500,)),
	       ("$90K - $99,999", (33000,)),
	       ("$100K - $124,999", (52000,)),
	       ("$125K - $149,999", (35000,)),
	       ("$150K - $174,999", (20500,)),
	       ("$175K - $199,999", (15000,)),
	       ("$200K - $249,999", (11000,)),
	       ("$250K - $299,999", (14500,)),
	       ("$300K - $349,999", (11000,)),
	       ("$350K - $399,999", (9500,)),
	       ("$400K - $499,999", (3500,)),
	       ("$500K - $749,999", (3500,)),
	       ("$750K - $999,999", (2000,)),
	       ("$1 MIL +", (900,)) )
    img = charter.getChart(values)
    img.save(name)
    return

# right half of a population pyramid
# data clumps of varying size
def test4(name='bartest.png'):
    w = 167
    h = 280
    measures = ( ('0', 0), ('2', 2000), ('4', 4000), ('6', 6000), ('8', 8000) )
    def color_mapping(vs):
	return map(lambda x: chart_colors.girl_pink, vs)
    charter = BarChart(w, h, measures, bar_width=2, 
		       barcolors=color_mapping, top_axis=True)
    values = (("85+", [900]),
	      ("70-84", [2100,2100,2100,2100,2100,2000,2000,2000,2000,2000,1900,1900,1900,1900]),
	      ("60-69", [5700,5700,4200,4200,4200,3000,3000,3500,3500]),
	      ("40-59", [3500,3500,3500,3500,4100,4100,4100,4100,4100,4100,5800,5800,5800,5800,5800,5800,4050,4050,4050]),
	      ("22-39", [6300,6300,6300,6300,7200,7200,7200,7200,7200,5900,5900,5900,5900,5000,5000,5000,5000]),
	      ("11-21", [3500,4500,5100,4500,4700,3900,3500,3700,4800,5500]),
	      ("0-10", [2500,3500,4100,3500,3700,2900,2500,2700,3800,4500]))
    img = charter.getChart(values)
    img.save(name)
    return

# left-handed population pyramid
def test5(name='bartest.png'):
    w = 167
    h = 280
    measures = ( ('0', 0), ('2', 2000), ('4', 4000), ('6', 6000), ('8', 8000) )
    def color_mapping(vs):
	return map(lambda x: chart_colors.boy_teal, vs)
    charter = BarChart(w, h, measures, bar_width=2, 
		       barcolors=color_mapping, top_axis=True, grow_left=True)
    values = (("85+", [900]),
	      ("70-84", [2100,2100,2100,2100,2100,2000,2000,2000,2000,2000,1900,1900,1900,1900]),
	      ("60-69", [5700,5700,4200,4200,4200,3000,3000,3500,3500]),
	      ("40-59", [3500,3500,3500,3500,4100,4100,4100,4100,4100,4100,5800,5800,5800,5800,5800,5800,4050,4050,4050]),
	      ("22-39", [6300,6300,6300,6300,7200,7200,7200,7200,7200,5900,5900,5900,5900,5000,5000,5000,5000]),
	      ("11-21", [3500,4500,5100,4500,4700,3900,3500,3700,4800,5500]),
	      ("0-10", [2500,3500,4100,3500,3700,2900,2500,2700,3800,4500]))
    img = charter.getChart(values)
    img.save(name)
    return

# does stuff line up correctly?
def test6(name='bartest.png'):
    w = 300
    h = 300
    measures = ( ('10', 10), )
    charter = BarChart(w, h, measures)
    values = ( ('five', (5,) ),
	       ('ten', (10,) ),
	       ('fifteen', (15,) )
	       )
    img = charter.getChart(values)
    img.save(name)
    return

if __name__ == '__main__':
    test6()

    
