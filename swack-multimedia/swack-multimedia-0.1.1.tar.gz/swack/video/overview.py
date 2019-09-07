import os

import cv2
import numpy as np


class VideoOverview(object):
    # cv2 的像素点按(b,g,r)的方式
    # 当原视频分辨率在16:9时，关闭shrink。提供shrink可以保持缩略图为原宽高比。
    version = "1.0.3"
    _margin_top = 200  # 顶部（200~300，需要刻视频信息）
    _margin_bottom = 30  # 底部（10~100）
    _margin_in = 10  # 内部（10~20）
    _margin_lr = 25  # 左右两侧（20~50）
    thumb_dpi_list = [(480, 270), (384, 216)]  # 16:9的几种合适的缩略图大小 1080p*0.25,1080p*0.2
    img_base_bgr = (127, 127, 127)  # 底图颜色
    capture = None
    thumbs_list = []

    def __init__(
            self,
            video,
            output="",
            thumb_dpi=None,
            w=4,
            h=10,
            shrink=None,
            show_rank=False,
            show_time=True,
            save_thumbs=False,
            save_result=True,
            ):
        self.video = video
        self.output = output if output else self.video + ".overview.png"
        self.w_thumb, self.h_thumb = thumb_dpi if thumb_dpi else self.thumb_dpi_list[0]
        self.w_layout = w
        self.h_layout = h
        self.shrink = self.__check_shrink(shrink)
        self.show_time = show_time  # 缩略图是否显示时间，默认True
        self.show_rank = show_rank  # 缩略图是否显示编号，默认False
        self.save_thumbs = save_thumbs
        self.save_result = save_result

        self.thumb_name = self.video + ".thumb_%02d_%02d.png"

    @staticmethod
    def __check_shrink(shrink):
        # 方案2：缩略图的分辨率按原视频等比缩小
        if isinstance(shrink, float):
            if 0.1 <= shrink <= 0.5:
                return shrink
        return None

    def _get_video_infos(self):
        # cv2 读取、计算
        print("\n>>>获取视频信息：")
        self.v_width = int(self.capture.get(3))  # 宽度
        self.v_height = int(self.capture.get(4))  # 高度
        self.v_fps = self.capture.get(5)  # 帧速率
        self.v_frame_count = int(self.capture.get(7))  # 视频文件的总帧数
        self.v_resolution = str(self.v_width) + " x " + str(self.v_height)
        self.v_duration = str(self.__seconds_to_hhmmss(int(self.v_frame_count) / self.v_fps))
        # os读取、计算
        self.v_basename = os.path.basename(self.video)
        self.v_size = self.__get_file_size(self.video)

        # 方案二：把视频缩略图大小按原视频大小缩小
        if self.shrink:
            self.w_thumb = int(self.shrink * self.v_width)
            self.h_thumb = int(self.shrink * self.v_height)

    @staticmethod
    def __get_file_size(video):
        stat = os.stat(video)
        size = stat.st_size
        size_str = "%d Bytes" % size
        if size > 1 * 1024 * 1024:  # MB
            size_str = "%.2f MB" % (size / 1024 / 1024)
        if size > 1 * 1024 * 1024 * 1024:  # GB
            size_str = "%.2f GB" % (size / 1024 / 1024 / 1024)
        return size_str

    @staticmethod
    def __seconds_to_hhmmss(seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return "%02d:%02d:%02d" % (h, m, s)

    def _calc_image_base(self):
        # 计算底图base的宽高，制作底图
        print("\n>>>生成底图：")
        w_base = self.w_thumb * self.w_layout + self._margin_in * (self.w_layout - 1) + self._margin_lr * 2
        h_base = self._margin_top + self.h_thumb * self.h_layout + self._margin_in * (self.h_layout - 1) + self._margin_bottom
        self.img_base = np.zeros((h_base, w_base, 3), dtype=np.uint8)
        self.img_base[:, :, 0:3] = self.img_base_bgr
        print("像素宽 : %d" % w_base)
        print("像素高 : %d" % h_base)

    def _calc_thumbnails(self):
        # 计算、分割、截取缩略图的信息
        print("\n>>>计算缩略图信息：")
        self.thumbnails = self.w_layout * self.h_layout
        sample = self.v_frame_count / (self.thumbnails + 1)  # 分割取样

        for num in range(self.thumbnails):
            h_array = int(num / self.w_layout)
            w_array = num % self.w_layout
            # 以下按像素在（行，列）的关系，对应像素xy为  x是列，y是行
            h_pos = h_array * self.h_thumb + h_array * self._margin_in + self._margin_top
            w_pos = w_array * self.w_thumb + w_array * self._margin_in + self._margin_lr
            name_pos = self.thumb_name % (h_array + 1, w_array + 1)  # 给人看的，按自然数1开始
            cur_frame = int(sample * (num + 1))
            cur_second = int(cur_frame / self.v_fps)
            cur_second_str = self.__seconds_to_hhmmss(cur_second)
            info = ((num + 1), h_pos, w_pos, name_pos, cur_frame, cur_second_str)
            print(info)
            # 自然顺序号，左上角坐标h，左上角坐标w，名字，当前帧数，当前秒数
            self.thumbs_list.append(info)

    def _split_thumbnails(self):
        # 分割缩略图，并刻编号、刻时间、保存缩略图
        print("\n>>>缩略图合并到底图：")
        for thumb in self.thumbs_list:
            num, h, w, name, frame, sec = thumb
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, frame)
            get, img = self.capture.read()
            if get:
                img_tmp = cv2.resize(img, (self.w_thumb, self.h_thumb), cv2.INTER_LINEAR)
                if self.show_time:  # 写入时刻？
                    cv2.putText(img_tmp, sec, (self.w_thumb - 150, 35), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 0, 255), 1)
                if self.show_rank:  # 写入编号？
                    cv2.putText(img_tmp, str(num), (10, 45), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 0, 127), 2)
                if self.save_thumbs:  # 保存缩略图？
                    cv2.imwrite(name, img_tmp)
                print("当前进度：%d/%d" % (num, self.thumbnails))
                self.img_base[h:h + self.h_thumb, w:w + self.w_thumb, :] = img_tmp

    def _get_header_infomation(self):
        print("\n>>>创建头部信息：")
        str_1 = "File Name  :  " + self.v_basename
        str_2 = "File Size   :  " + self.v_size
        str_3 = "Resolution :  " + self.v_resolution
        str_4 = "Duration   :  " + self.v_duration
        # 头部刻字与字形、字号、坐标位置、线宽，布局w、缩略图分辨率,等多个参数相关
        # 以下参数在w>=3，缩略图分辨率>=384*216时效果较好
        cv2.putText(self.img_base, str_1, (30, 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
        cv2.putText(self.img_base, str_2, (30, 80), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
        cv2.putText(self.img_base, str_3, (30, 120), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
        cv2.putText(self.img_base, str_4, (30, 160), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

    def _save_result(self):
        if self.save_result:
            print("\n>>>最终结果存档至：%s" % self.output)
            cv2.imwrite(self.output, self.img_base)
            return
        else:
            print("\n>>>用户设置为最终结果不存档！")

    def run(self):
        self.capture = cv2.VideoCapture(self.video)
        if not self.capture.isOpened():
            print("\n>>>无法打开指定文件！")
            return 1  # 打开视频失败
        self._get_video_infos()
        self._calc_image_base()
        self._calc_thumbnails()
        self._split_thumbnails()
        self._get_header_infomation()
        self._save_result()
        print("\n>>>全部结束。")
        return 0
