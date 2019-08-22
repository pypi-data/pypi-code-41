# -*- coding: utf-8 -*-
import bencode

__all__ = ('torrent')


class torrent:
    def __init__(self, file):
        with open(file, 'rb') as f:
            b = f.read()
        self.info = bencode.decode(b)

    def add_tracker(self, trackers, reserved_tracker=True):
        """
        添加 Tracker 信息

        :param list trackers: tracker 服务器地址列表
        :param bool reserved_tracker: 是否保留原有的 tracker 服务器地址，默认为 True
        """
        tracker_source_list = self.info['announce-list']

        if reserved_tracker:
            tracker_list = trackers + tracker_source_list
            tracker_list = [i if isinstance(i, list) else [i] for i in tracker_list]
        else:
            tracker_list = trackers
        new_tracker_list = []
        for i in tracker_list:
            if i not in new_tracker_list:
                new_tracker_list.append(i)
        self.info['announce-list'] = new_tracker_list

    def save_torrent(self, file):
        """
        保存文件

        :param file: 文件保存路径
        """
        with open(file, 'wb') as f:
            f.write(bencode.encode(self.info))


if __name__ == '__main__':
    t1 = torrent('1.torrent')
    t1.add_tracker(['udp://208.83.20.20:6969/announce'])
    t1.save_torrent('2.torrent')
