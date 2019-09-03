import hashlib
import json
import logging
import os
import re
import time
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
import requests
from PIL import Image
from skimage import data as sk_data
from skimage import draw, transform
from skimage.feature import match_template
from tqdm import tqdm

from .sqlite_orm import GetData
from .set_logger import set_logger
from .sqlite_model import ImageTemplate, ReplaceImages


class ImreplTool(object):

    def __init__(self, cover_up=False, cover_with_img=False, cover_color=None, log_level=None, optimize_t_sequence=True):
        super(ImreplTool, self).__init__()
        log_level = logging.INFO if log_level is None else log_level

        self.LOGGER = set_logger(log_level)
        self._db = GetData(self.LOGGER)

        self.OTS = optimize_t_sequence
        self.FINAL_SCORE = dict()
        self._scores = list()
        self._ids = dict()
        self._template_id_img_dic = dict()
        self._templates = dict()
        self._threshold_values = dict()
        self._template_names = list()
        self._temp_hashes = set()
        self._repl_hashes = set()
        self._image_show = None
        self._cover_up = cover_up
        self._cover_with_img = cover_with_img
        self._cover_color = cover_color

        # 数值控制区，注意取值越大越有可能超出图像边界
        self.EP_METHOD = False  # encircling picking method 是否启用三点包围取点法， False 则启用直线取点法
        self.EP_DISTANCE = 3  # 三点包围取点法的像素取点距离
        self.SP_PIX = 3  # straight picking method 直线取点法的像素取点数
        self.BORDER_EXTEND = 8  # 匹配边界的覆盖扩展像素数
        self.KEEP_COVER_IMG_SCALE = True  # 填充logo是否保持原比例
        self.REPLACE_IMG_ARRAY = dict()   # 填充logo的 array 对象
        self.CONCENTRATION = 100  # 填充透明度（尚不完善）
        self.COVER_TEMPLATES = None  # 若设置了cover_up_with_img=True，可选择覆盖哪些模板的匹配图像 (匹配上哪个模板，则使用数据库中相应的替换logo替换)

    def add_templates(self, templates, update_if_existed=False):
        """
        将模板加入数据库
        :param templates: 二维列表： [['bp', '/home/host/images/image_1.jpg', 85], [ ... ], ...]
                                      ↑                 ↑                   ↑
                                  模板名称            模板路径               阈值

        :param update_if_existed: 若库中已存在则覆盖
        :return:
        """
        if not isinstance(templates, list) and not isinstance(templates[0], list):
            raise ValueError('expect a 2D list, please check your inputs')
        self.LOGGER.info('start to process the template images')
        db_hash_data = self._db.get(model_name='ImageTemplate', key_list=['hash_str'])
        self._temp_hashes.update({x.hash_str for x in db_hash_data}) if db_hash_data else {}
        at = tqdm(total=len(templates))
        for tp in templates:
            t_name, t_path, t_thr = tp
            t_thr = int(t_thr)
            if t_thr < 0 or t_thr > 100:
                raise ValueError('threshold value should be between 0 - 100')
            t_thr = 80 if t_thr == 0 else t_thr
            self._save_t_array_in_db(name=t_name, f_path=t_path, threshold=t_thr, update_it=update_if_existed)
            at.update()
        at.close()
        self.LOGGER.info('process complete')

    def add_replace_img(self, repl_paths):
        """
        将替换图片加入数据库
        :param repl_paths: 二维列表： [['bp', '/home/host/images/image_1.jpg'], [ ... ], ...]
                                      ↑                 ↑
                                  模板名称            模板路径
        :return:
        """
        if not isinstance(repl_paths, list) and not isinstance(repl_paths[0], list):
            raise ValueError('expect a 2D list, please check your inputs')
        self.LOGGER.info('start to process the replace images')
        repl_hash_data = self._db.get(model_name='ReplaceImages', key_list=['hash_str'])
        self._repl_hashes.update({x.hash_str for x in repl_hash_data}) if repl_hash_data else {}
        at = tqdm(total=len(repl_paths))
        for tp in repl_paths:
            t_name, t_path = tp
            self._save_repl_array_in_db(name=t_name, f_path=t_path)
            at.update()
        at.close()
        self.LOGGER.info('process complete')

    def initialize_data(self, template_names=None):
        self.LOGGER.info('initializing templates in database')
        if isinstance(template_names, str):
            template_names = [template_names]
        if template_names is not None and not isinstance(template_names, list):
            raise ValueError('template_names expect a list or string, not {}'.format(self._type_str(template_names)))
        self._template_names = template_names
        t_raw = list()
        for tn in template_names:
            db_data = self._db.get(model_name='ImageTemplate',
                                   key_list=['id', 'data', 'threshold'],
                                   filter_dic={'template_type': tn, 'status': '1'})
            if db_data:
                t_raw.append(db_data)
        for each_t in t_raw:
            self._threshold_values.update({template_names[t_raw.index(each_t)]: list(map(lambda x: int(x.threshold) / 100, each_t))})
            if self.OTS:
                self._ids.update({template_names[t_raw.index(each_t)]: list(map(lambda x: int(x.id), each_t))})
                self._template_id_img_dic.update({str(x.id): np.array(json.loads(x.data)) for x in each_t})
                self._templates.update({template_names[t_raw.index(each_t)]: list(map(lambda x: np.array(json.loads(x.data)), each_t))})

        if self._cover_with_img:
            db_repl_data = self._db.get(model_name='ReplaceImages', key_list=['repl_type', 'data'], filter_dic={'status': 1})
            self.COVER_TEMPLATES = {x.repl_type for x in db_repl_data} if self.COVER_TEMPLATES is None else self.COVER_TEMPLATES if db_repl_data else dict()
            self.REPLACE_IMG_ARRAY.update({x.repl_type: np.array(json.loads(x.data), dtype=np.uint8) for x in db_repl_data if x.repl_type in self.COVER_TEMPLATES})
        self.LOGGER.info('templates initialized')

    def check(self, img_path):
        if isinstance(img_path, str):
            self.FINAL_SCORE = dict()
            im_bio = self._get_image_io(img_path)
            img = self._load_img(f_io=im_bio, as_gray=True)
            self._image_show = self._load_img(f_io=im_bio)

            result_dic = dict()
            score_list = list()
            count_out = 0
            for i_type in self._template_names:
                template_lis = self._templates.get(i_type)
                count_in = 0
                score_dic = dict()
                best_score = list()
                type_ = False
                id_list = self._ids.get(i_type)
                threshold_values = self._threshold_values.get(i_type)
                for cot, template_img in enumerate(template_lis):
                    threshold_value = threshold_values[cot]
                    tmp_id = id_list[count_in]
                    result = self._get_result_score(template_array=template_img, image_array=img)
                    score = result.max() if result is not None else 0
                    score = round(score, 4)
                    best_score.append(score)
                    score_dic[str(tmp_id)] = score
                    if score and score > threshold_value:
                        type_ = True
                        if self._cover_up:
                            ij = np.unravel_index(np.argmax(result), result.shape)
                            x, y = ij[::-1]
                            tem_h, tem_w = template_img.shape
                            self._color_gradient_filth(im_bio, x, y, tem_h, tem_w, i_type)
                        break
                    count_in += 1
                count_out += 1
                if type_:
                    score_list.append(score_dic)
                result_dic[i_type] = type_
                self.FINAL_SCORE.update({i_type: max(best_score)})
            self._scores.append(score_list)
            im_bio.close()
            return result_dic

    def show(self):
        if self._image_show is not None:
            plt.imshow(self._image_show, plt.cm.gray)
            plt.show()

    def save(self, file_path=None):
        if self._image_show is not None:
            if file_path:
                plt.imsave(file_path, self._image_show)
                return True
            else:
                bio = BytesIO()
                plt.imsave(bio, self._image_show)
                return bio
        return False

    def optimizing_template_sequence(self):
        if self._scores:
            self.LOGGER.info('start to optimizing templates sequences')
            count_dic = dict()
            for each_pic_score_lis in self._scores:
                for each_type_temps in each_pic_score_lis:
                    for tem in each_type_temps:
                        if count_dic.get(tem):
                            count_dic[tem].append(each_type_temps.get(tem))
                        else:
                            count_dic[tem] = list()
                            count_dic[tem].append(each_type_temps.get(tem))
            count_dic = {x: sum(count_dic.get(x)) for x in count_dic}
            re_order = list()
            for type_ids in self._ids:
                id_dic = dict()
                for t_id in type_ids:
                    count_dic_tid_value = count_dic.get(str(t_id))
                    if count_dic_tid_value:
                        id_dic[str(t_id)] = round(count_dic_tid_value, 4)

                new_order_lis = [x for x in sorted(id_dic, key=id_dic.__getitem__, reverse=True)]
                old_order_lis = [int(x) for x in new_order_lis]
                old_order_lis.sort(reverse=False)

                re_order.append(new_order_lis)

                id_count = 0
                for i in old_order_lis:
                    new_id = new_order_lis[id_count]
                    data = json.dumps(self._template_id_img_dic.get(str(new_id)))

                    self._db.update(
                        model_name='',
                        update_dic={'data': data},
                        filter_dic={'id': str(i)}
                    )
                    id_count += 1

            self.LOGGER.info('optimizing sequences done! ')

    def _get_result_score(self, template_array, image_array):
        result = None
        try:
            result = match_template(image_array, template_array)
        except ValueError as e:
            self.LOGGER.error('sth wrong when matching the template : {}'.format(e))
        finally:
            return result

    def _color_gradient_filth(self, image_bio, x, y, shape_h, shape_w, temp_name):

        def get_replace_color(P):
            if replace_image is not None:
                replace_x = int(x + 0.5 * (w - replace_img_newsize[1]))
                replace_y = int(y + 0.5 * (h - replace_img_newsize[0]))

                replace_next_x = int(replace_x + replace_img_newsize[1])
                replace_next_y = int(replace_y + replace_img_newsize[0])

                if replace_x <= P[0] < replace_next_x and replace_y <= P[1] < replace_next_y:
                    get_x = P[0] - replace_x
                    get_y = P[1] - replace_y

                    replace_img_colors = list(replace_img_pix[get_x, get_y])
                    alfa = replace_img_colors[3]
                    if alfa != 0:
                        return replace_img_colors
            return None

        def add_replace_color(base_color, repl_color, concentration=100):
            alfa = repl_color[3]
            alfa = int((concentration // 100) * alfa)

            bR = base_color[0]
            bG = base_color[1]
            bB = base_color[2]

            rR = repl_color[0]
            rG = repl_color[1]
            rB = repl_color[2]

            R = int((bR * (255 - alfa) + (rR * alfa)) / 255)
            G = int((bG * (255 - alfa) + (rG * alfa)) / 255)
            B = int((bB * (255 - alfa) + (rB * alfa)) / 255)

            color_added = [R, G, B]
            return color_added

        def straight_picking(point, direction, pix):
            r_lis = list()
            g_lis = list()
            b_lis = list()
            for i in range(1, pix + 1):
                if direction == 'u':
                    p = [point[0], point[1] - i]
                elif direction == 'r':
                    p = [point[0] + i, point[1]]
                elif direction == 'b':
                    p = [point[0], point[1] + i]
                else:
                    p = [point[0] - i, point[1]]

                if p[0] >= max_width or p[1] >= max_height:
                    break
                p_color = list(image_pix[p[0], p[1]])
                # print('p_color:', p_color)
                p_color_r, p_color_g, p_color_b = p_color
                r_lis.append(p_color_r)
                g_lis.append(p_color_g)
                b_lis.append(p_color_b)
            # print('r_lis:', r_lis, 'g_lis:',g_lis, 'b_lis:', b_lis)
            if len(r_lis) + len(g_lis) + len(b_lis) > 0:
                avg_color = [
                    sum(r_lis) // len(r_lis),
                    sum(g_lis) // len(g_lis),
                    sum(b_lis) // len(b_lis)]
            else:
                avg_color = None
            return avg_color

        def encircling_picking(point, direction, distance):
            if direction == 'u':
                pa = [point[0] - distance, point[1]]
                pb = [point[0] + distance, point[1]]
                pc = [point[0], point[1] - distance]
            elif direction == 'r':
                pa = [point[0], point[1] - distance]
                pb = [point[0] + distance, point[1]]
                pc = [point[0], point[1] + distance]
            elif direction == 'b':
                pa = [point[0] - distance, point[1]]
                pb = [point[0] + distance, point[1]]
                pc = [point[0], point[1] + distance]
            else:
                pa = [point[0], point[1] - distance]
                pb = [point[0], point[1] + distance]
                pc = [point[0] - distance, point[1]]

            if pa[0] <= 0 or pa[0] >= max_width or pa[1] <= 0 or pa[1] >= max_height:
                pa = None
            if pb[0] <= 0 or pb[0] >= max_width or pb[1] <= 0 or pb[1] >= max_height:
                pb = None
            if pc[0] <= 0 or pc[0] >= max_width or pc[1] <= 0 or pc[1] >= max_height:
                pc = None
            pa_color = None
            pb_color = None
            pc_color = None
            if pa:
                pa_color = list(image_pix[pa[0], pa[1]])
            if pb:
                pb_color = list(image_pix[pb[0], pb[1]])
            if pc:
                pc_color = list(image_pix[pc[0], pc[1]])
            if pa_color and pb_color and pc_color:
                avg_color = [
                    (pa_color[0] + pb_color[0] + pc_color[0]) // 3,
                    (pa_color[1] + pb_color[1] + pc_color[1]) // 3,
                    (pa_color[2] + pb_color[2] + pc_color[2]) // 3]
            elif pa_color and pb_color and not pc_color:
                avg_color = [
                    pa_color[0] + pb_color[0] // 2,
                    pa_color[1] + pb_color[1] // 2,
                    pa_color[2] + pb_color[2] // 2,
                ]
            elif pa_color and pc_color and not pb_color:
                avg_color = [
                    pa_color[0] + pc_color[0] // 2,
                    pa_color[1] + pc_color[1] // 2,
                    pa_color[2] + pc_color[2] // 2,
                ]
            elif pb_color and pc_color and not pa_color:
                avg_color = [
                    pb_color[0] + pc_color[0] // 2,
                    pb_color[1] + pc_color[1] // 2,
                    pb_color[2] + pc_color[2] // 2,
                ]
            elif pb_color and not pc_color and not pa_color:
                avg_color = pb_color

            elif pc_color and not pb_color and not pa_color:
                avg_color = pc_color

            elif pa_color and not pc_color and not pb_color:
                avg_color = pa_color
            else:
                avg_color = None
            return avg_color

        def mix_colors(U, R, B, L, point):
            """
            —————————————————————
            |         |a        |
            |---------o---------|
            |    b    |   d     |
            |         |c        |
            —————————————————————

            """
            a = point[1] - y_extended
            b = point[0] - x_extended
            c = shape_h - a
            d = shape_w - b
            if U and B:
                UBr = (U[0] + (((B[0] - U[0]) / shape_h) * (point[1] - y_extended)))
                UBg = (U[1] + (((B[1] - U[1]) / shape_h) * (point[1] - y_extended)))
                UBb = (U[2] + (((B[2] - U[2]) / shape_h) * (point[1] - y_extended)))
            elif U and not B:
                UBr = U[0]
                UBg = U[1]
                UBb = U[2]
            elif B and not U:
                UBr = B[0]
                UBg = B[1]
                UBb = B[2]
            else:
                UBr = None
                UBg = None
                UBb = None
            if R and L:
                RLr = (L[0] + (((R[0] - L[0]) / shape_w) * (point[0] - x_extended)))
                RLg = (L[1] + (((R[1] - L[1]) / shape_w) * (point[0] - x_extended)))
                RLb = (L[2] + (((R[2] - L[2]) / shape_w) * (point[0] - x_extended)))
            elif R and not L:
                RLr = R[0]
                RLg = R[1]
                RLb = R[2]
            elif L and not R:
                RLr = L[0]
                RLg = L[1]
                RLb = L[2]
            else:
                RLr = None
                RLg = None
                RLb = None

            if a <= shape_h // 2 and b <= shape_w // 2:
                if UBr and RLr:
                    if a + b != 0:
                        mix_r = int(UBr + (((RLr - UBr) / (b + a)) * a))
                        mix_g = int(UBg + (((RLg - UBg) / (b + a)) * a))
                        mix_b = int(UBb + (((RLb - UBb) / (b + a)) * a))
                        p_mix = [mix_r, mix_g, mix_b]
                    else:
                        p_mix = list(image_pix[x_extended, y_extended])
                elif UBr and not RLr:
                    if a + b != 0:
                        mix_r = int(UBr)
                        mix_g = int(UBg)
                        mix_b = int(UBb)
                        p_mix = [mix_r, mix_g, mix_b]
                    else:
                        p_mix = list(image_pix[x_extended, y_extended])
                elif RLr and not UBr:
                    if a + b != 0:
                        mix_r = int(RLr)
                        mix_g = int(RLg)
                        mix_b = int(RLb)
                        p_mix = [mix_r, mix_g, mix_b]
                    else:
                        p_mix = list(image_pix[x_extended, y_extended])
                else:
                    p_mix = [255, 255, 255]

            elif a > shape_h // 2 and b <= shape_w // 2:
                if UBr and RLr:
                    if b + c != 0:
                        mix_r = int(UBr + (((RLr - UBr) / (c + b)) * c))
                        mix_g = int(UBg + (((RLg - UBg) / (c + b)) * c))
                        mix_b = int(UBb + (((RLb - UBb) / (c + b)) * c))
                        p_mix = [mix_r, mix_g, mix_b]
                    else:
                        p_mix = list(image_pix[x_extended, y_extended + shape_h])
                elif UBr and not RLr:
                    if a + b != 0:
                        mix_r = int(UBr)
                        mix_g = int(UBg)
                        mix_b = int(UBb)
                        p_mix = [mix_r, mix_g, mix_b]
                    else:
                        p_mix = list(image_pix[x_extended, y_extended + shape_h])
                elif RLr and not UBr:
                    if a + b != 0:
                        mix_r = int(RLr)
                        mix_g = int(RLg)
                        mix_b = int(RLb)
                        p_mix = [mix_r, mix_g, mix_b]
                    else:
                        p_mix = list(image_pix[x_extended, y_extended + shape_h])
                else:
                    p_mix = [255, 255, 255]

            elif a > shape_h // 2 and b > shape_w // 2:
                if UBr and RLr:
                    if d + c != 0:
                        mix_r = int(UBr + (((RLr - UBr) / (c + d)) * c))
                        mix_g = int(UBg + (((RLg - UBg) / (c + d)) * c))
                        mix_b = int(UBb + (((RLb - UBb) / (c + d)) * c))
                        p_mix = [mix_r, mix_g, mix_b]
                    else:
                        p_mix = list(
                            image_pix[x_extended + shape_w, y_extended + shape_h])
                elif UBr and not RLr:
                    if a + b != 0:
                        mix_r = int(UBr)
                        mix_g = int(UBg)
                        mix_b = int(UBb)
                        p_mix = [mix_r, mix_g, mix_b]
                    else:
                        p_mix = list(
                            image_pix[x_extended + shape_w, y_extended + shape_h])
                elif RLr and not UBr:
                    if a + b != 0:
                        mix_r = int(RLr)
                        mix_g = int(RLg)
                        mix_b = int(RLb)
                        p_mix = [mix_r, mix_g, mix_b]
                    else:
                        p_mix = list(
                            image_pix[x_extended + shape_w, y_extended + shape_h])
                else:
                    p_mix = [255, 255, 255]

            else:
                if UBr and RLr:
                    if d + a != 0:
                        mix_r = int(UBr + (((RLr - UBr) / (a + d)) * a))
                        mix_g = int(UBg + (((RLg - UBg) / (a + d)) * a))
                        mix_b = int(UBb + (((RLb - UBb) / (a + d)) * a))
                        p_mix = [mix_r, mix_g, mix_b]
                    else:
                        p_mix = list(image_pix[x_extended + shape_w, y_extended])
                elif UBr and not RLr:
                    if a + b != 0:
                        mix_r = int(UBr)
                        mix_g = int(UBg)
                        mix_b = int(UBb)
                        p_mix = [mix_r, mix_g, mix_b]
                    else:
                        p_mix = list(image_pix[x_extended + shape_w, y_extended])
                elif RLr and not UBr:
                    if a + b != 0:
                        mix_r = int(RLr)
                        mix_g = int(RLg)
                        mix_b = int(RLb)
                        p_mix = [mix_r, mix_g, mix_b]
                    else:
                        p_mix = list(image_pix[x_extended + shape_w, y_extended])
                else:
                    p_mix = [255, 255, 255]
            return p_mix

        replace_image = self.REPLACE_IMG_ARRAY.get(temp_name)
        x_extended = int(x) - self.BORDER_EXTEND
        y_extended = int(y) - self.BORDER_EXTEND
        h = shape_h
        w = shape_w
        if replace_image is not None:
            replace_img_resized = self._resize_img(
                img=replace_image, size_control=[
                    h, w], keep_scale=self.KEEP_COVER_IMG_SCALE)
            replace_newsize_img = replace_img_resized[0]
            replace_img_newsize = replace_img_resized[1]
            bio = BytesIO()
            plt.imsave(bio, replace_newsize_img)
            replace_img_rgb = Image.open(bio)
            replace_img_pix = replace_img_rgb.load()
        shape_h = int(shape_h) + (self.BORDER_EXTEND * 2)
        shape_w = int(shape_w) + (self.BORDER_EXTEND * 2)
        image_rgb = Image.open(image_bio)
        image_pix = image_rgb.load()
        max_height = image_rgb.height
        max_width = image_rgb.width
        for Y in range(y_extended, y_extended + shape_h + 1):
            for X in range(x_extended, x_extended + shape_w + 1):
                P = [X, Y]
                p_up = None
                p_right = None
                p_butt = None
                p_left = None
                if y_extended >= 0:
                    p_up = [X, y_extended]
                if x_extended + shape_w <= max_width:
                    p_right = [x_extended + shape_w, Y]
                if y_extended + shape_h <= max_height:
                    p_butt = [X, y_extended + shape_h]
                if x_extended >= 0:
                    p_left = [x_extended, Y]

                p_up_color = None
                p_right_color = None
                p_butt_color = None
                p_left_color = None
                if self.EP_METHOD:
                    if p_up:
                        p_up_color = encircling_picking(
                            p_up, direction='u', distance=self.EP_DISTANCE)
                    if p_right:
                        p_right_color = encircling_picking(
                            p_right, direction='r', distance=self.EP_DISTANCE)
                    if p_butt:
                        p_butt_color = encircling_picking(
                            p_butt, direction='b', distance=self.EP_DISTANCE)
                    if p_left:
                        p_left_color = encircling_picking(
                            p_left, direction='l', distance=self.EP_DISTANCE)
                else:
                    # print(p_up, p_right, p_butt, p_left)
                    if p_up:
                        p_up_color = straight_picking(
                            p_up, direction='u', pix=self.SP_PIX)
                    if p_right:
                        p_right_color = straight_picking(
                            p_right, direction='r', pix=self.SP_PIX)
                    if p_butt:
                        p_butt_color = straight_picking(
                            p_butt, direction='b', pix=self.SP_PIX)
                    if p_left:
                        p_left_color = straight_picking(
                            p_left, direction='l', pix=self.SP_PIX)

                p_color = mix_colors(
                    p_up_color,
                    p_right_color,
                    p_butt_color,
                    p_left_color,
                    P)
                replace_color = get_replace_color(P)
                if replace_color:
                    p_color = add_replace_color(
                        base_color=p_color,
                        repl_color=replace_color,
                        concentration=self.CONCENTRATION)
                elif self._cover_color:
                    p_color = self._cover_color
                draw_x = np.array([X, X + 1, X + 1, X])
                draw_y = np.array([Y, Y, Y + 1, Y + 1])
                rr, cc = draw.polygon(draw_y, draw_x)
                draw.set_color(self._image_show, [rr, cc], p_color)

    def _save_t_array_in_db(self, name, f_path, threshold=None, update_it=False):
        im_bio = self._get_image_io(f_path)
        img_array = self._load_img(f_io=im_bio, as_gray=True)
        sk_array_str = str(img_array.tolist())

        threshold = 80 if threshold is None else threshold
        hash_data = self._hash_str(sk_array_str)
        if hash_data not in self._temp_hashes:
            add_d = {
                'hash_str': hash_data,
                'template_type': name,
                'data': sk_array_str,
                'threshold': threshold,
                'status': 1
            }
            self._db.add(model=ImageTemplate, add_dic=add_d)
        elif update_it and hash_data in self._temp_hashes:
            self._db.update(
                model_name='template_type',
                update_dic={'template_type': name, 'data': sk_array_str, 'threshold': threshold},
                filter_dic={'hash_str': hash_data}
            )

    def _save_repl_array_in_db(self, name, f_path):
        im_bio = self._get_image_io(f_path)
        img_array = self._load_img(f_io=im_bio)
        sk_array_str = str(img_array.tolist())

        hash_data = self._hash_str(sk_array_str)
        if hash_data not in self._repl_hashes:
            add_d = {'hash_str': hash_data, 'repl_type': name, 'data': sk_array_str, 'status': 1}
            self._db.add(model=ReplaceImages, add_dic=add_d)

    @staticmethod
    def _load_img(f_io, as_gray=False, as_grey=None):
        if as_grey is not None:
            as_gray = as_grey
        sk_data.use_plugin('pil')
        return sk_data.imread(f_io, as_gray=as_gray)

    @staticmethod
    def _resize_img(img, size_control, keep_scale=True):
        """
        :param img:
        :param size_control:    [高, 宽]
        :param keep_scale:
        :return:
        """
        height = img.shape[0]
        width = img.shape[1]
        if not keep_scale:
            new_h = size_control[0]
            new_w = size_control[1]
        else:
            scale = height / width
            new_h = size_control[0]
            new_w = int(new_h / scale)
            if new_w > size_control[1]:
                new_w = size_control[1]
                new_h = scale * new_w

        new_size = (int(new_h), int(new_w))
        new_size_img = transform.resize(image=img, output_shape=new_size)
        return new_size_img, [new_h, new_w]

    @staticmethod
    def _get_image_io(url):
        if re.findall('^https?://', url):
            res = requests.request("GET", url)
            img = res.content
        else:
            if not re.findall('^/', url):
                base_path = os.getcwd()
                path = os.path.join(base_path, url)
            else:
                path = url
            with open(path, 'rb') as rf:
                img = rf.read()
        bio = BytesIO()
        bio.write(img)
        return bio

    @staticmethod
    def _type_str(thing):
        _type = re.findall('\'([^\']+)\'', str(type(thing)))[0]

    @staticmethod
    def _hash_str(data):
        """
        生成hash的方法封装  用于生产固定字符串的hash值
        :param data: 字符串
        :return hash: 字符串hash值
        """
        md5 = hashlib.md5()
        md5.update(str(data).encode('utf-8'))
        return md5.hexdigest()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instances'):
            cls._instances = super(ImreplTool, cls).__new__(cls)
        return cls._instances

    def __del__(self):
        if self.OTS:
            self.optimizing_template_sequence()
        self.LOGGER.info('all work complete')


if __name__ == "__main__":
    image_list = [
        # 'http://chuantu.xyz/t6/702/1565924123x2890171859.jpg',  # SJZG
        'images/shijuezhongguo_1.jpg',   # SJZG
        'images/shijuezhongguo_3.jpeg',   # SJZG
    ]

    t_lis = list()

    # ------------------------ 实例化 ---------------------------
    IT = ImreplTool(cover_up=True, cover_with_img=True)
    template_paths = [
        ['SJZG', 'templates/shijuezhongguo_template_1.jpg', 81],
        ['SJZG', 'templates/shijuezhongguo_template_4.jpg', 82],
    ]
    replacements = [
        ['SJZG', 'replacement/611_logo.png'],
    ]
    # IT.add_templates(templates=template_paths)
    # IT.add_replace_img(repl_paths=replacements)
    IT.initialize_data(template_names=['SJZG'])
    # ----------------------------------------------------------

    for count, image in enumerate(image_list):
        t1 = time.time()

        # ---------实际调用-------------
        check_result = IT.check(image)
        IT.show()
        IT.save('replace_img_{}.jpg'.format(count))
        # -----------------------------

        t2 = time.time()
        t_total = t2 - t1
        t_lis.append(t_total)
        m, s = divmod(t_total, 60)
        h, m = divmod(m, 60)
        print(check_result, IT.FINAL_SCORE, "%d:%02d:%s" % (h, m, round(s, 2)))

    # match_image.optimizing_template_sequence()
    if len(t_lis) > 0:
        print()
        t_avg = sum(t_lis) / len(t_lis)
        m, s = divmod(t_avg, 60)
        h, m = divmod(m, 60)
        print("time_avg: ", "%d:%02d:%s" % (h, m, round(s, 2)))
