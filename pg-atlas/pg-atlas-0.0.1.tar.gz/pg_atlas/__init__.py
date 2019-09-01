name = 'pg_atlas'

import json
import pygame


class PGAtlas:
    """
    Atlas class for easiest work with TexturePacker`s sprite sheets.
    Ones loaded, atlas will create pygame.image by calling the name of frame in json file.
    Json file can be created in TexturePacker program.
    """
    def __init__(self, path: str = None):
        self.source_data = None
        self.source_file = None

        if path:
            self.add_source(path)

    def add_source(self, path: str):
        """
        Add source to empty Atlas object.
        :param path:
        :return:
        """
        with open(path, 'r') as json_data:
            self.source_data = json.load(json_data)
            image_name = path.split('.')[-2] + '.png'
            self.source_file = pygame.image.load(image_name)

    def create_image(self, frame_name: str):
        """
        Creates pygame.image from Atlas by calling the name of frame in json file.
        :param frame_name:
        :return:
        """
        if self.source_data and self.source_file:
            row = self.source_data['frames'][frame_name]['frame']
            return self.source_file.subsurface(row['x'], row['y'], row['w'], row['h'])
        else:
            raise Exception('Source file is not loaded. Call add_source(path) method with existing file path.')

    def create_image_list(self, images: list):
        """
        Creates list of images by list of string names.
        :param images:
        :return:
        """
        return [self.create_image(image_name) for image_name in images]
