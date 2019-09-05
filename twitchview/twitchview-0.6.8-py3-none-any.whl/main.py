#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    https://gitlab.com/aspellip/twitchview

import configparser
import tkinter as tk
from io import BytesIO
import json
import os
import random
import subprocess
import sys
import threading
import traceback
import urllib.request
import urllib.error
import urllib.parse
from functools import partial

import m3u8
from PIL import Image, ImageTk

from twitchview.irc import main as ircchat

__version__ = "0.6.8"


class AppTk(tk.Tk):
    def __init__(self, parent, config):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.cfg = configparser.ConfigParser()
        self.cfg.read(config + 'config.ini')
        self.config_path = config
        # This token you can get on a URL http://tw.fex.cc
        self.token = self.cfg.get('twitch', 'token')
        self.nick = self.cfg.get('twitch', 'nick')
        self.debug = self.cfg.get('twitch', 'debug')
        self.player = self.cfg.get('twitch', 'player')
        self.tw_url = "https://api.twitch.tv/kraken/streams/followed"
        self.usher_api = 'https://usher.ttvnw.net/api/channel/hls/{channel}.m3u8?player=twitchweb' + \
                         '&token={token}&sig={sig}&$allow_audio_only=true&allow_source=true' + \
                         '&type=any&p={random}'
        self.token_api = 'https://api.twitch.tv/api/channels/{channel}/access_token?oauth_token='
        self.logo_size = 32, 32
        self.create_menubar()
        self.initialize()

    def print_debug(self, message):
        if self.debug == "on":
            print(message)

    @staticmethod
    def url_request(url, token):
        data = {"Authorization": "OAuth %s" % token, 'Accept': 'application/vnd.twitchtv.v5+json'}
        req = urllib.request.Request(url, headers=data)
        response = urllib.request.urlopen(req)
        return response

    def get_token_and_signature(self, channel):
        try:
            url = self.token_api.format(channel=channel)
            response = urllib.request.urlopen('%s%s' % (url, self.token))
            data = json.load(response)
        except urllib.error.HTTPError as e:
            self.print_debug(e)
            return False
        sig = data['sig']
        token = urllib.parse.quote(data['token'])
        return token, sig

    def get_live_stream(self, channel):
        token, sig = self.get_token_and_signature(channel)
        r = random.randint(0, 1E7)
        try:
            url = self.usher_api.format(channel=channel, sig=sig, token=token, random=r)
            response = urllib.request.urlopen(url)

        except urllib.error.URLError as e:
            self.print_debug(e)
            return False
        data = response.read().decode("utf-8")

        m3u8_obj = m3u8.loads(data)
        return m3u8_obj

    @staticmethod
    def print_video_urls(m3u8_obj):
        quality = {}
        try:
            for p in m3u8_obj.playlists:
                quality[p.media[0].name.split(' ', 1)[0]] = p.uri
        except KeyError:
            traceback.print_exc()
            sys.exit(3)
        return quality

    def create_menubar(self):
        menubar = tk.Menu(self)
        filemenu = tk.Menu(self, menubar, tearoff=0)
        filemenu.add_command(label="Reload", command=self.restart_ui, accelerator="Ctrl+Shift+R")

        filemenu.add_separator()

        filemenu.add_command(label="Exit", command=self.destroy_ui, accelerator="Ctrl+Shift+Q")
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About...", command=self.create_window_about)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.config(menu=menubar)
        self.bind_all("<Control-R>", self.restart_ui)
        self.bind_all("<Control-Q>", self.destroy_ui)

    def get_twitch_favorite(self):
        try:
            response = self.url_request(self.tw_url, self.token)
            data = json.load(response)
            return data
        except urllib.error.HTTPError as e:
            self.print_debug(e)
            return None

    def worker(self, i, j):
        # Get logo images of streamers and resize them
        img_data = BytesIO(urllib.request.urlopen(i['channel']['logo']).read())
        image = Image.open(img_data)
        image.thumbnail(self.logo_size, Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image.convert("RGB"))

        tw_col = {
            'status': i['channel']['status'],
            'name': i['channel']['name'],
            'game': i['game'],
            'viewers': i['viewers']
        }
        # Logo is a first in a row.
        label_img = tk.Label(self, image=photo, justify=tk.LEFT)
        label_img.image = photo
        label_img.grid(row=j, column=0)

        for k, col in enumerate(tw_col.values()):
            try:
                col = str(col)
                self.print_debug(col)
                tk.Label(self, text=col[:64], justify=tk.LEFT).grid(row=j, column=k + 1, sticky=tk.W)
            except tk.TclError:
                tk.Label(self, text=":)", justify=tk.LEFT).grid(row=j, column=k + 1, sticky=tk.W)

        # Button is a last in a row
        self.print_debug(tw_col.values())
        m3u8_obj = self.get_live_stream(tw_col['name'])
        
        q_buttons = self.print_video_urls(m3u8_obj)
        v = tk.StringVar(self)
        v.set(list(q_buttons.keys())[0])
        tk.OptionMenu(self, v, *q_buttons.keys()).grid(row=j, column=len(tw_col) + 2 + 1, sticky=tk.W)
        tk.Button(self, text="Play", justify=tk.LEFT,
                  command=partial(self.button_play_stream, q_buttons, v)).grid(row=j, column=len(tw_col) + 4,
                                                                               sticky=tk.W)
        tk.Button(self, text="Chat", justify=tk.LEFT,
                  command=partial(self.button_chat, tw_col['name'])).grid(row=j, column=len(tw_col) + 5, sticky=tk.W)

    def initialize(self):
        streamers = self.get_twitch_favorite()
        try:
            if streamers['streams'] is not None:
                threads = []
                for j, i in enumerate(streamers['streams']):
                    t = threading.Thread(target=self.worker, args=(i, j,))
                    threads.append(t)
                    t.start()
            else:
                tk.Label(self, text="No channels available in list",
                         justify=tk.LEFT).grid()
        except TypeError:
            tk.Label(self, text="Wrong token in %sconfig.ini OR twitch servers unavailable" % self.config_path,
                     justify=tk.LEFT).grid()

    def button_play_stream(self, uri, quality):
        quality = quality.get()
        uri = uri[quality]
        self.print_debug(quality)
        if "nt" == os.name:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.Popen(
                [self.player, uri,
                 quality], startupinfo=startupinfo,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE)
        else:
            subprocess.Popen(
                [self.player, uri,
                 quality], stderr=subprocess.PIPE,
                stdout=subprocess.PIPE)

    def button_chat(self, tw_name):
        ircchat(self.nick, self.token, "#%s" % tw_name)

    def create_window_about(self):
        t = tk.Toplevel(self)
        t.wm_title("About...")
        lw = tk.Label(t, text="This is twitchview v%s\n src: https://gitlab.com/aspellip/twitchview" % __version__)
        lw.pack(side="top", fill="both", expand=True, padx=100, pady=100)

    def restart_ui(self, event=""):
        self.print_debug("Restarting .... %s" % event)
        self.destroy()
        main()

    def destroy_ui(self, event=""):
        self.print_debug("Quit .... %s" % event)
        self.destroy()


def check_config():
    home_dir = os.environ['HOME'] + "/.twitchview/"
    config_file = home_dir + "config.ini"
    if not os.path.exists(home_dir):
        os.makedirs(home_dir)
    if not os.path.exists(config_file):
        from shutil import copyfile
        copyfile("config.ini.example", config_file)
    return home_dir


def main():
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    config = check_config()
    app = AppTk(None, config)
    app.title('Twitch View')
    if "nt" == os.name:
        app.wm_iconbitmap(bitmap="icon.ico")
    else:
        app.wm_iconbitmap(bitmap="@icon.xbm")
    app.mainloop()


if __name__ == "__main__":
    main()
