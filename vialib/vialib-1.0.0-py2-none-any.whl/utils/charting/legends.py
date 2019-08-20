
import Image, ImageDraw, ImageFont
import chart_colors

import inspect
import sys
import os

def execution_path(filename):
      return os.path.join(os.path.dirname(inspect.getfile(sys._getframe(1))), filename)

RELATIVE_PATH = "fonts/ARIAL.TTF"
arial_font = ImageFont.truetype(execution_path(RELATIVE_PATH), 10)

def base_image(w, h):
    return Image.new('RGB', (w, h), chart_colors.white)

def simple_legend(attrcolors, img, x, y, center_x=False, boxh=8, boxw=22, font=arial_font):
    draw = ImageDraw.ImageDraw(img)

    tx = x
    ty = y
    for spec in attrcolors:
	if len(spec) == 2:
	    (attr, color) = spec

	    (lw, lh) = draw.textsize(attr, font=font)
	
            total_w = lw + boxw + 6
            if center_x:
                  sx = tx - (total_w/2)
            else:
                  sx = tx

	    boxx = sx
	    boxy = ty 
	
	    lx = sx + boxw + 6
	    ly = ty

	    draw.rectangle((boxx, boxy, boxx+boxw, boxy+boxh),
			   fill=color)
	    draw.text((lx, ly), attr, font=font, fill=chart_colors.black)

	    ty += lh + 6
	elif len(spec) == 1:
	    attr = spec[0]

	    (lw, lh) = draw.textsize(attr, font=font)

            if center_x:
                  lx = tx - (lw/2)
            else:
                  lx = tx
	    ly = ty

	    draw.text((lx, ly), attr, font=font, fill=chart_colors.black)

	    ty += lh + 6

    return img

def pct(v):
    return ("%.0f" % (float(v)*100.0)) + '%'

# this code is taken from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/499351
# though i changed the default separators to American style    
def format_number(number, precision=0, group_sep=',', decimal_sep='.', font=arial_font):

    number = ('%.*f' % (max(0, precision), number)).split('.')

    integer_part = number[0]
    if integer_part[0] == '-':
        sign = integer_part[0]
        integer_part = integer_part[1:]
    else:
        sign = ''
      
    if len(number) == 2:
        decimal_part = decimal_sep + number[1]
    else:
        decimal_part = ''
   
    integer_part = list(integer_part)
    c = len(integer_part)
   
    while c > 3:
        c -= 3
        integer_part.insert(c, group_sep)

    return sign + ''.join(integer_part) + decimal_part

def drawDottedLineDown(draw, xy, length):
    (x, y) = xy
    ey = y + length
    while y < ey:
	draw.point((x, y), fill=chart_colors.dot_color)
	draw.point((x, y+1), fill=chart_colors.dot_color)
	y += 3
    return

def drawDottedLineAcross(draw, xy, length):
    (x, y) = xy
    ex = x + length
    while x < ex:
	draw.point((x, y), fill=chart_colors.dot_color)
	draw.point((x+1, y), fill=chart_colors.dot_color)
	x += 3
    return

def empl_status_legend(values, img, x, y, font=arial_font):
    draw = ImageDraw.ImageDraw(img)

    total_out = values['Not in labor force']
    employed = values['Employed']
    unemployed = values['Unemployed']
    armed_forces = values['Armed Forces']
    total_in = employed + unemployed
    total = total_in + total_out + armed_forces
    
    bigboxw = 18
    bigboxh = 18
    smallboxw = 10
    smallboxh = 10

    tx = x
    ty = y
    
    tx = x + 4
    ty = y + 4
    draw.rectangle((tx, ty, tx + bigboxw, ty + bigboxh), fill=chart_colors.tan)
    label = 'Not in labor force'
    (lw, lh) = draw.textsize(label, font=font)
    tx = x + 30
    ty = ty + bigboxh/2 - lh/2
    draw.text((tx, ty), label, font=font, fill=chart_colors.black)
    number = format_number(total_out)
    (lw, lh) = draw.textsize(number, font=font)
    tx = x + 195 - lw
    draw.text((tx, ty), number, font=font, fill=chart_colors.black)
    npct = pct(total_out / float(total))
    (lw, lh) = draw.textsize(npct, font=font)
    tx = x + 232 - lw
    draw.text((tx, ty), npct, font=font, fill=chart_colors.black)    

    tx = x + 4
    ty = y + 4 + bigboxh + 4
    draw.rectangle((tx, ty, tx + bigboxw, ty + bigboxh), fill=chart_colors.sep_pie_color)
    draw.rectangle((tx + 4, ty + 4, tx + bigboxw - 4, ty + bigboxh - 4), fill=chart_colors.white)
    label = 'Civilian labor force'
    (lw, lh) = draw.textsize(label, font=font)
    tx = x + 30
    ty = ty + bigboxh/2 - lh/2
    draw.text((tx, ty), label, font=font, fill=chart_colors.black)
    number = format_number(total_in)
    (lw, lh) = draw.textsize(number, font=font)
    tx = x + 195 - lw
    draw.text((tx, ty), number, font=font, fill=chart_colors.black)
    npct = pct(total_in / float(total))
    (lw, lh) = draw.textsize(npct, font=font)
    tx = x + 232 - lw
    draw.text((tx, ty), npct, font=font, fill=chart_colors.black) 

    tx = x + 4 + bigboxw/2
    ty = y + 4 + ((bigboxh + 4) * 2)
    drawDottedLineDown(draw, (tx, ty), 13)
    drawDottedLineAcross(draw, (tx, ty+13), 20)

    tx = x + 32
    ty = y + 4 + ((bigboxh + 4) * 2) + 8
    draw.rectangle((tx, ty, tx + smallboxw, ty + smallboxh), fill=chart_colors.boy_teal)
    label = 'Employed'
    (lw, lh) = draw.textsize(label, font=font)
    tx = x + 52
    ty = ty + smallboxh/2 - lh/2
    draw.text((tx, ty), label, font=font, fill=chart_colors.gray_75)
    number = format_number(employed)
    (lw, lh) = draw.textsize(number, font=font)
    tx = x + 195 - lw
    draw.text((tx, ty), number, font=font, fill=chart_colors.gray_75)
    npct = pct(employed / float(total))
    (lw, lh) = draw.textsize(npct, font=font)
    tx = x + 232 - lw
    draw.text((tx, ty), npct, font=font, fill=chart_colors.gray_75) 

    tx = x + 4 + bigboxw/2
    ty = y + 4 + ((bigboxh + 4) * 2) + 8 + smallboxh
    drawDottedLineDown(draw, (tx, ty), 13)
    drawDottedLineAcross(draw, (tx, ty+13), 20)

    tx = x + 32
    ty = y + 4 + ((bigboxh + 4) * 2) + 8 + smallboxh + 8
    draw.rectangle((tx, ty, tx + smallboxw, ty + smallboxh), fill=chart_colors.mustard)
    label = 'Unemployed'
    (lw, lh) = draw.textsize(label, font=font)
    tx = x + 52
    ty = ty + smallboxh/2 - lh/2
    draw.text((tx, ty), label, font=font, fill=chart_colors.gray_75)
    number = format_number(unemployed)
    (lw, lh) = draw.textsize(number, font=font)
    tx = x + 195 - lw
    draw.text((tx, ty), number, font=font, fill=chart_colors.gray_75)
    npct = pct(unemployed / float(total))
    (lw, lh) = draw.textsize(npct, font=font)
    tx = x + 232 - lw
    draw.text((tx, ty), npct, font=font, fill=chart_colors.gray_75) 
   
#    tx = x + 4 + bigboxw/2
    ty = y + 4 + ((bigboxh + 4) * 2) + ((smallboxh + 8) * 2) + 4
#    drawDottedLineDown(draw, (tx, ty), 13)
#    drawDottedLineAcross(draw, (tx, ty+13), 20)

    tx = x + 4
#    ty = y + 4 + bigboxh + 4
    draw.rectangle((tx, ty, tx + bigboxw, ty + bigboxh), fill=chart_colors.light_green)
    label = 'In Armed Forces'
    (lw, lh) = draw.textsize(label, font=font)
    tx = x + 30
    ty = ty + bigboxh/2 - lh/2
    draw.text((tx, ty), label, font=font, fill=chart_colors.black)
    number = format_number(armed_forces)
    (lw, lh) = draw.textsize(number, font=font)
    tx = x + 195 - lw
    draw.text((tx, ty), number, font=font, fill=chart_colors.black)
    npct = pct(armed_forces / float(total))
    (lw, lh) = draw.textsize(npct, font=font)
    tx = x + 232 - lw
    draw.text((tx, ty), npct, font=font, fill=chart_colors.black) 

    return 

def totals_legend(attrvalues, attrcolors, attrs, img, x, y, font=arial_font):
    draw = ImageDraw.ImageDraw(img)

    sum = 0.0
    for attr in attrs:
	value = float(attrvalues[attr])
	sum += value

    tx = x + 2
    ty = y + 2
    for label in attrs: 
	(lw, lh) = draw.textsize(label, font=font)
	draw.rectangle((tx, ty, tx+16, ty+16), fill=attrcolors[label])
	ly = ty + 16 - lh/2
	draw.text((tx+25, ty), label, font=font, fill=chart_colors.black)

	number = format_number(float(attrvalues[label]))
	(lw, lh) = draw.textsize(number, font=font)
	draw.text((x+186-lw, ty), number, font=font, fill=chart_colors.black)

	npct = pct(float(attrvalues[label]) / sum)
	(lw, lh) = draw.textsize(npct, font=font)
	draw.text((x+223-lw, ty), npct, font=font, fill=chart_colors.black)

	ty += 16 + 8

    return

def aggregate_legend(attrcolors, img, x, y, box_h=15, box_w=15, line_h=5, line_w=15, font=arial_font):
    text_gap = 5
    secondary_gap = 50
    draw = ImageDraw.ImageDraw(img)
		
    (primary_name, primary_color) = attrcolors[0] 
    (lw, lh) = draw.textsize(primary_name, font=font)
	
    draw.rectangle((x, y, x+box_w, y+box_h), fill=primary_color)
    draw.text((x+box_w+text_gap, y), primary_name, font=font, fill=chart_colors.black)

    x += box_w + text_gap + lw + secondary_gap
    for secondary in attrcolors[1:]:
	(name, color) = secondary
    	(lw, lh) = draw.textsize(name, font=font)
	ty = y + lh/4
	draw.rectangle((x, ty, x+line_w, ty+line_h), fill=color)
	draw.text((x+line_w+text_gap, y), name, font=font, fill=chart_colors.black)
	x += box_w + text_gap * 5 + lw
	
    return img
