# -*- coding: utf-8 -*-

from orbis_eval import app
from orbis_eval.libs import files
from .build_html import build

import os
from palettable.tableau import Tableau_20
from operator import itemgetter


class Main(object):

    def __init__(self, rucksack):

        super(Main, self).__init__()
        self.rucksack = rucksack
        self.config = self.rucksack.open['config']
        self.data = self.rucksack.open['data']
        self.pass_name = self.rucksack.open['config']['file_name'].split(".")[0]
        self.folder = os.path.join(app.paths.output_path, "html_pages", self.pass_name)
        self.queue = self.sort_queue(self.rucksack.get_keys())

    def sort_queue(self, queue):
        int_queue = []

        for item in queue:
            try:
                int_queue.append(int(item))
            except ValueError:
                int_queue.append(item)
        int_queue = sorted(int_queue)

        new_queue = [str(item) for item in int_queue]

        return new_queue


    def get_keys(self, item):

        keys = set()
        if item.get('gold'):
            for entity in item['gold']:
                keys.add(entity['key'])

        if item.get('computed'):
            for entity in item['computed']:
                keys.add(entity['key'])
        return keys

    def get_sf_colors(self, keys):

        sf_colors = {}
        colour_idx = 0
        for sf in keys:
            sf_colors[sf] = Tableau_20.hex_colors[colour_idx]
            colour_idx = 0 if colour_idx == 19 else colour_idx + 1
        return sf_colors

    def run(self):

        app.logger.info("Building HTML pages")

        timestamp = files.get_timestamp()
        folder_dir = os.path.join(self.folder + f"-{timestamp}")
        files.create_folder(folder_dir)
        pages = {}

        for item_key in self.queue:
            app.logger.info(f"Building Page: {item_key}")
            item = self.rucksack.itemview(item_key)

            try:
                next_item = self.queue[self.queue.index(item_key) + 1]
            except IndexError:
                next_item = None

            try:
                previous_item = self.queue[self.queue.index(item_key) - 1]
            except IndexError:
                previous_item = None

            key = item['index']
            sf_colors = self.get_sf_colors(self.get_keys(item))
            html, html_blocks = build(self.config, self.rucksack, item, next_item, previous_item, sf_colors)

            pages[key] = html_blocks

            file_dir = os.path.join(folder_dir, str(key) + ".html")
            app.logger.debug(file_dir)
            with open(file_dir, "w") as open_file:
                open_file.write(html)

        app.logger.info("Finished building HTML pages")
        return pages
