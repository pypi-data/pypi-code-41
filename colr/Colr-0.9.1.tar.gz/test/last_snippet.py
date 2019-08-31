from colr.name_data import get_x11_rgb
from colr import Colr
x_names = get_x11_rgb(fix_names=True)
print(Colr('test', x_names['aquamarine']))
