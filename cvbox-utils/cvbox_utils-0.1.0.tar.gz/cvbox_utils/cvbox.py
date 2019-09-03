class Box(object):
    def __init__(self, box, mode='xyxy',dtype=int):
        super(Box, self).__init__()
        if box.__class__.__name__=='Box':
            for name,value in vars(box).items():
                setattr(self, name, value)
            return
        self.box = list(map(dtype, box))
        self.mode = mode
        self.dtype = dtype
        if mode not in ('xyxy', 'xywh', 'cxywh'):
            print("Not support mode: {}. ('xyxy', 'xywh', 'cxywh' ONLY.)".format(mode))
            raise NotImplementedError

    def xyxy(self):
        if self.mode=='xyxy':
            return self.box
        elif self.mode=='xywh':
            self.box = [self.box[0], self.box[1], self.box[0]+self.box[2], self.box[1]+self.box[3]]
            return self.box
        elif self.mode=='cxywh':
            self.box = [self.dtype(self.box[0]-self.box[2]/2.), self.dtype(self.box[1]-self.box[3]/2.), self.dtype(self.box[0]+self.box[2]/2.), self.dtype(self.box[1]+self.box[3]/2.)]
        self.mode = 'xyxy'
        return self.box

    def xywh(self):
        if self.mode=='xywh':
            return self.box
        elif self.mode=='xyxy':
            self.box = [self.box[0], self.box[1], -self.box[0]+self.box[2], -self.box[1]+self.box[3]]
        elif self.mode=='cxywh':
            self.box = [self.dtype(self.box[0]-self.box[2]/2.), self.dtype(self.box[1]-self.box[3]/2.), self.box[2], self.box[3]]
        self.mode = 'xywh'
        return self.box

    def cxywh(self):
        if self.mode=='cxywh':
            return self.box
        elif self.mode=='xyxy':
            self.box = [self.dtype(-self.box[0]/2.+self.box[2]/2.), self.dtype(-self.box[1]/2.+self.box[3]/2.), -self.box[0]+self.box[2], -self.box[1]+self.box[3]]
        elif self.mode=='xywh':
            self.box = [self.dtype(self.box[0]+self.box[2]/2.), self.dtype(self.box[1]+self.box[3]/2.), self.box[2], self.box[3]]
        self.mode = 'cxywh'
        return self.box

    def __getitem__(self, index):
        return self.box[index]
    
    def __len__(self):
        return len(self.box)

    def __str__(self):
        return "Box({}, mode='{}', dtype='{}')".format(self.box, self.mode, self.dtype.__name__)

    def add_field(self, field_name, value):
    	setattr(self, field_name, value)

    def get_field(self, field_name):
    	return getattr(self, field_name)

class BoxList(object):
    def __init__(self, boxlist, mode='xyxy', dtype=int):
        if boxlist.__class__.__name__=='BoxList':
            for name,value in vars(boxlist).items():
                setattr(self, name, value)
            return
        self.boxes = [Box(b, mode, dtype) for b in boxlist]

    def __getitem__(self, index):
        return self.boxes[index]

    def __len__(self):
        return len(self.boxes)

    def __str__(self):
        info_list = [b.__str__() for b in self.boxes]
        return 'BoxList(\n' + ',\n'.join(info_list) + '\n)'

    def add_field(self, field_name, value):
        setattr(self, field_name, value)

    def get_field(self, field_name):
        return getattr(self, field_name)


