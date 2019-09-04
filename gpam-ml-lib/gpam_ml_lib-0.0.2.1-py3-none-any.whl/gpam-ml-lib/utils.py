import numpy as np
import cv2


def resize_imgs(list_path_img=[], img_shape=(256, 256)):
    list_new_imgs = []
    for img in list_path_img:
        read_img = cv2.imread(img)
        read_img = cv2.cvtColor(read_img, cv2.COLOR_BGR2RGB)
        read_img = cv2.resize(read_img, img_shape)
        list_new_imgs.append(read_img)

    return list_new_imgs


def rle2mask(rle, imgshape):
    width = imgshape[0]
    height = imgshape[1]

    mask = np.zeros(width*height).astype(np.uint8)

    array = np.asarray([int(x) for x in rle.split()])
    starts = array[0::2]
    lengths = array[1::2]

    current_position = 0
    for index, start in enumerate(starts):
        mask[int(start):int(start+lengths[index])] = 1
        current_position += lengths[index]

    return np.flipud(np.rot90(mask.reshape(height, width), k=1))


def mask2rle(img):
    tmp = np.rot90(np.flipud(img), k=3)
    rle = []
    lastColor = 0
    startpos = 0
    endpos = 0

    tmp = tmp.reshape(-1, 1)
    for i in range(len(tmp)):
        if (lastColor == 0) and tmp[i] > 0:
            startpos = i
            lastColor = 1
        elif (lastColor == 1) and (tmp[i] == 0):
            endpos = i-1
            lastColor = 0
            rle.append(str(startpos)+' '+str(endpos-startpos+1))
    return " ".join(rle)
