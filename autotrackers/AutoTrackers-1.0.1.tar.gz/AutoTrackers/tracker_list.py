# -*- coding: utf-8 -*-

from urllib import request

__all__ = ('tracker_list_url', 'get_tracker_list')

# tracker_list_url 来自 https://github.com/ngosang/trackerslist
tracker_list_url = {'best': 'https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt',
                    'all': 'https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all.txt',
                    'udp': 'https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all_udp.txt',
                    'http': 'https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all_http.txt',
                    'https': 'https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all_https.txt',
                    'ws': 'https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all_ws.txt',
                    'best_ip': 'https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best_ip.txt',
                    'all_ip': 'https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all_ip.txt'}


def get_tracker_list(url):
    response = request.urlopen(url)
    html = response.read()
    html = html.decode("utf-8").rstrip().split('\n\n')
    return html
