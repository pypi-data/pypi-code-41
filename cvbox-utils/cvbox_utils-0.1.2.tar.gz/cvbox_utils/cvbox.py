import torch

class BoxList(object):
    def __init__(self, boxes, dtype=torch.float32, mode='xyxy'):
        if boxes.__class__.__name__=='BoxList':
            for name,value in vars(box).items():
                setattr(self, name, value)
            return
        if boxes.__class__.__name__=='torch.Tensor':
            self.dtype = boxes.dtype
        else:
            self.dtype = dtype
        try:
            self.box = torch.tensor(boxes, dtype=self.dtype)
        except:
            print('cannot convert box to torch.tensor.')
            raise
        try:
            assert (len(self.box.shape)== 1 and self.box.shape[0]==4) or self.box.shape[1] == 4
        except:
            print('BoxList have to be initailized by a nx4 tensor')
            raise
        self.mode = mode
        
        if mode not in ('xyxy', 'xywh', 'cxywh'):
            print("Not support mode: {}. ('xyxy', 'xywh', 'cxywh' ONLY.)".format(mode))
            raise NotImplementedError

    def xyxy(self):
        if self.mode=='xyxy':
            return self.box
        elif self.mode=='xywh':
            box = torch.stack([self.box[:,0], self.box[:,1], self.box[:,0]+self.box[:,2], self.box[:,1]+self.box[:,3]], dim=1)
        elif self.mode=='cxywh':
            box = torch.stack([self.box[:,0]-self.box[:,2]/2., self.box[:,1]-self.box[:,3]/2., self.box[:,0]+self.box[:,2]/2., self.box[1]+self.box[:,3]/2.], dim=1)
        return box

    def _xyxy(self):
        self.box = self.xyxy()
        self.mode = 'xyxy'
        return self.box

    def xywh(self):
        if self.mode=='xywh':
            return self.box
        elif self.mode=='xyxy':
            box = torch.stack([self.box[:,0], self.box[:,1], -self.box[:,0]+self.box[:,2], -self.box[:,1]+self.box[:,3]], dim=1)
        elif self.mode=='cxywh':
            box = torch.stack([self.box[:,0]-self.box[:,2]/2., self.box[:,1]-self.box[:,3]/2., self.box[:,2], self.box[:,3]], dim=1)
        return box

    def _xywh(self):
        self.box = self.xywh()
        self.mode = 'xywh'
        return self.box

    def cxywh(self):
        if self.mode=='cxywh':
            return self.box
        elif self.mode=='xyxy':
            box = torch.stack([(self.box[:,0]+self.box[:,2])/2., (self.box[:,1]+self.box[:,3])/2., -self.box[:,0]+self.box[:,2], -self.box[:,1]+self.box[:,3]], dim=1)
        elif self.mode=='xywh':
            box = torch.stack([self.box[:,0]+self.box[:,2]/2., self.box[:,1]+self.box[:,3]/2., self.box[:,2], self.box[:,3]], dim=1)
        return box

    def _cxywh(self):
        self.box = self.cxywh()
        self.mode = 'cxywh'
        return self.box

    def __getitem__(self, index):
        return self.box[index]
    
    def __len__(self):
        return len(self.box)

    def __str__(self):
        return "BoxList({}, mode='{}', dtype='{}')".format(self.box, self.mode, self.dtype)

    def add_field(self, field_name, value):
    	setattr(self, field_name, value)

    def get_field(self, field_name):
    	return getattr(self, field_name)


if __name__=='__main__':
    a = BoxList([1,2,3,4], mode='xywh', dtype=torch.int)
    print('xyxy', a.xyxy())
    print('xywh', a.xywh())
    print('cxywh', a.cxywh())


