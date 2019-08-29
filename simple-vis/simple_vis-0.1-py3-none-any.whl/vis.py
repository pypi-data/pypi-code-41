import matplotlib.pyplot as plt

__all__ = ['imshow', 'Plot']


def imshow(winname, input_array, shape=None, title=None, cmap=None, shareaxis=True, pltshow=True, pause=0.0001):
    if not isinstance(input_array, (tuple, list)):
        plt.figure(num=winname)
        plt.suptitle(winname)
        plt.title(title)
        img = check_img(input_array)
        plt.imshow(img, cmap)
    
    else:
        num = len(input_array)
        shape = check_shape_equ(shape, num)
        cmap = check_str_equ(cmap, num)
        title = check_str_equ(title, num)
        
        fig = plt.figure(num=title, figsize=(shape[1] * 3, shape[0] * 3 + 0.5))
        fig.clf()
        fig.suptitle(winname)
        fig.subplots(shape[0], shape[1], sharex=shareaxis, sharey=shareaxis)
        axes = fig.get_axes()
        
        for i in range(shape[0]):
            for j in range(shape[1]):
                idx = i * shape[1] + j
                ax = axes[idx]
                ax.set_title(title[idx])
                img = input_array[idx]
                img = check_img(img)
                ax.imshow(img, cmap[idx])
    
    if pltshow:
        plt.ion()
        plt.show()
        plt.pause(pause)


class Plot():
    def __init__(self, winname, shape, title=None, cmap=None, shareaxis=True):
        shape = check_shape(shape)
        
        num = shape[0] * shape[1]
        self.cmap = check_str_equ(cmap, num)
        self.title = check_str_equ(title, num)
        self.shape = shape
        
        fig = plt.figure(num=winname, figsize=(shape[1] * 3, shape[0] * 3 + 0.5))
        fig.clf()
        fig.suptitle(winname)
        
        fig.subplots(shape[0], shape[1], sharex=shareaxis, sharey=shareaxis)
        axes = fig.get_axes()
        
        self.fig = fig
        self.axes = axes
    
    def set_data(self, input_array):
        if not isinstance(input_array, (tuple, list)):
            input_array = (input_array,)
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                idx = i * self.shape[1] + j
                axes = self.axes[idx]
                img = input_array[idx]
                img = check_img(img)
                
                axes.clear()
                axes.set_title(self.title[idx])
                axes.imshow(img, self.cmap[idx])
    
    def show(self, pause=0.0001):
        plt.ion()
        plt.show()
        plt.pause(pause)
    
    def save(self, filename, dpi=100):
        self.fig.savefig(filename, dpi=dpi)


def check_img(img):
    if len(img.shape) == 3:
        if len(img.shape[2]) == 1:
            img = img.reshape((img.shape[1], img.shape[2]))
        elif len(img.shape[2]) != 3 and len(img.shape[2]) != 4:
            raise ValueError(f'the image of dims must be "HWC", and C expected 3 or 4, but got {img.shape}')
    
    elif len(img.shape) != 2:
        raise ValueError(f'expected image of shape is 2 or 3, but got {img.shape}')
    
    return img


def check_str_equ(string, num):
    if string is not None:
        if isinstance(string, (tuple, list)):
            assert len(string) == num
        elif isinstance(string, str):
            string = (string,) * num
        else:
            raise TypeError(f'expected str, tuple or list (got {type(string).__name__})')
    else:
        string = (string,) * num
    return string


def check_shape_equ(shape, num):
    if shape is not None:
        if isinstance(shape, (tuple, list)):
            assert len(shape) == 2 and shape[0] * shape[1] == num
        elif isinstance(shape, int):
            assert shape == num
            shape = (1, shape)
        else:
            raise TypeError(f'expected int, tuple or list (got {type(shape).__name__})')
    else:
        shape = (1, num)
    return shape


def check_shape(shape):
    if isinstance(shape, int):
        shape = (1, shape)
    elif isinstance(shape, (tuple, list)):
        if len(shape) == 1:
            shape = (1, *shape)
        elif len(shape) != 2:
            raise ValueError(f'expected len(shape) is 2, but got {len(shape)}')
    else:
        raise TypeError(f'expected int, tuple or list (got {type(shape).__name__})')
    return shape
