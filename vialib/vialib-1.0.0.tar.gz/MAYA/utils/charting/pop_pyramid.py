
import Image, ImageDraw, ImageFont

import bar_chart2
import chart_colors

class PopulationPyramidChart:

    def __init__(self, 
		 width,
		 height,
		 measures,
		 left_barcolors=None,
		 right_barcolors=None):
	self.width = width
	self.height = height
	right_w = width/2
	left_w = width/2
	
	self.right_charter = bar_chart2.BarChart(right_w,
						 height,
						 measures,
						 bar_width=2,
						 barcolors=right_barcolors,
						 top_axis=False,
						 grow_left=False,
						 jam=True)
	self.left_charter = bar_chart2.BarChart(left_w,
						height,
						measures,
						bar_width=2,
						barcolors=left_barcolors,
						top_axis=False,
						grow_left=True,
						jam=True)
	
    def getHistogram(self, charter, values, total_w, line_values=None):
	stub_img = Image.new('RGB',
			     (0, 0),
			     chart_colors.white)
	draw = ImageDraw.Draw(stub_img)

	(label_maxw, label_maxh) = charter.getMaxLabelSizes(draw, charter.attrs, charter.yfont)
	(measure_label_maxw, measure_label_maxh) = charter.getMaxLabelSizes(draw, charter.getMeasureLabels(), charter.xfont)
	n_measures = len(charter.getMeasureLabels())

	ind_axis_w = label_maxw + (charter.label_gutter * 2) + 2
	dep_axis_w = (total_w / 2)
	dep_axis_xoffset = ind_axis_w / 2
	dep_axis_h = measure_label_maxh + (charter.label_gutter * 2) + 1
	ind_axis_h = charter.height - (dep_axis_h*2)

	dep_axis_img = charter.getDependentAxis(dep_axis_w, dep_axis_h, 
						dep_axis_xoffset, values)
	if charter.top_axis:
	    top_dep_axis_img = charter.getDependentAxis(dep_axis_w,
							dep_axis_h,
							dep_axis_xoffset,
							values,
							top=True)

	canvas_w = (total_w - ind_axis_w) / 2
	canvas_h = charter.height - (dep_axis_h*2)
	
	canvas_img = charter.getCanvas(values, canvas_w, canvas_h, line_values)
	
	chart_img = Image.new('RGB',
			      (dep_axis_w, charter.height),
			      chart_colors.white)

	if charter.grow_left:
	    if charter.top_axis:
		chart_img.paste(top_dep_axis_img, (0, 0))
		chart_img.paste(dep_axis_img, (0, canvas_h + dep_axis_h))
		chart_img.paste(canvas_img, (0, dep_axis_h))	
	    else:
		chart_img.paste(dep_axis_img, (0, canvas_h + dep_axis_h))
		chart_img.paste(canvas_img, (0, dep_axis_h))	
	else:
	    if charter.top_axis:
		chart_img.paste(top_dep_axis_img, (0, 0))
		chart_img.paste(dep_axis_img, (0, canvas_h + dep_axis_h))
		chart_img.paste(canvas_img, (ind_axis_w/2, dep_axis_h))	
	    else:
		chart_img.paste(dep_axis_img, (0, canvas_h + dep_axis_h))
		chart_img.paste(canvas_img, (ind_axis_w/2, dep_axis_h))	

	return (chart_img, ind_axis_w, dep_axis_h)

    def getIndependentAxis(self, charter, values, w, h):
	ind_axis_img = Image.new('RGB', (w, h), chart_colors.white)
	draw = ImageDraw.Draw(ind_axis_img)
	
	labels = charter.attrs
	for label in labels:
	    (sy, ey) = charter.getClumpPosition(h, label, values)
	    y = (sy+ey)/2
	    (lw, lh) = draw.textsize(label, font=charter.yfont)
	    y -= (lh/2)
	    x = (w - lw)/2 
	    draw.text((x, y), label, font=charter.yfont, fill=chart_colors.black)

	draw.line((0, 0, 0, h-1), fill=chart_colors.axis_color)
	draw.line((w-1, 0, w-1, h-1), fill=chart_colors.axis_color)

	return ind_axis_img


    def getChart(self, left_values, right_values, line_values={}):
	left_line_values = line_values.get('left_line_values')
	right_line_values = line_values.get('right_line_values')

	chart_img = Image.new('RGB',
			      (self.width, self.height),
			      chart_colors.white)
	draw = ImageDraw.Draw(chart_img)

	left_values = self.left_charter.processValues(left_values)
	right_values = self.right_charter.processValues(right_values)

	(left_img, ind_axis_w, dep_axis_h) = self.getHistogram(self.left_charter, 
							       left_values,
							       self.width,
							       left_line_values)
	(right_img, ind_axis_w, dep_axis_h) = self.getHistogram(self.right_charter,
								right_values,
								self.width,
								right_line_values)

	ind_axis_img = self.getIndependentAxis(self.left_charter,
					       left_values, ind_axis_w, 
					       self.height - (dep_axis_h*2))
	
	chart_img.paste(left_img, (0, 0))
	chart_img.paste(right_img, (self.width/2, 0))
	chart_img.paste(ind_axis_img, ((self.width-ind_axis_w)/2, dep_axis_h))

	return chart_img

def test1(name='bartest.png'):
    w = 390
    h = 280
    measures = ( ('0', 0), ('2', 2000), ('4', 4000), ('6', 6000), ('8', 8000) )
    def left_color_mapping(vs):
	return map(lambda x: chart_colors.boy_teal, vs)
    def right_color_mapping(vs):
	return map(lambda x: chart_colors.girl_pink, vs)
    charter = PopulationPyramidChart(w, h, measures,  
				     left_barcolors=left_color_mapping, 
				     right_barcolors=right_color_mapping)
    values = (("85+", [900]),
	      ("70-84", [2100,2100,2100,2100,2100,2000,2000,2000,2000,2000,1900,1900,1900,1900]),
	      ("60-69", [5700,5700,4200,4200,4200,3000,3000,3500,3500]),
	      ("40-59", [3500,3500,3500,3500,4100,4100,4100,4100,4100,4100,5800,5800,5800,5800,5800,5800,4050,4050,4050]),
	      ("22-39", [6300,6300,6300,6300,7200,7200,7200,7200,7200,5900,5900,5900,5900,5000,5000,5000,5000]),
	      ("11-21", [3500,4500,5100,4500,4700,3900,3500,3700,4800,5500]),
	      ("0-10", [2500,3500,4100,3500,3700,2900,2500,2700,3800,4500]))
    img = charter.getChart(values, values, 
			   { 'left_line_values': values,
			     'right_line_values': values }
			   )
    img.save(name)
    return

if __name__ == '__main__':
    test1()
