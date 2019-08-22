from PIL.Image import Image
from PIL import Image as ImageFactory

from random import randint
from typing import List, Optional, Iterable, Tuple

from os import walk
from os.path import join, exists

from logging import Logger

from datasetutils.pasting import PastingRule, DefaultPastingRule
from datasetutils.mutations import MutationProcessor

class Box(object):
    def __init__(self, minx, miny, width, height):
        self.minx = minx
        self.miny = miny
        self.width = width
        self.height = height

    def __iter__(self) -> Iterable[Tuple[int, int, int, int]]:
        yield from [self.minx, self.miny, self.width, self.height]

    def __str__(self) -> str: 
        return str({
            "MinX": self.minx, 
            "MinY": self.miny, 
            "Width": self.width, 
            "Height": self.height, 
        })

class MixedObject(object):
    def __init__(self, image : Image, box : Box):
        self.__image = image
        self.__box = box

    @property
    def image(self) -> Image:
        return self.__image

    @property
    def box(self) -> Box:
        return self.__box

    def __iter__(self) -> Iterable[Tuple[Image, Box]]:
        yield from [self.image, self.box]

class MixInDataset(object):

    def __init__(self, root: str, mixing : str, to_mix_with : str, logger : Optional[Logger] = None):

        if not all([root, mixing, to_mix_with]):
            raise ValueError(f"Some of the arguments were set to null or empty (root, mixing, to_mix_with):{(root, mixing, to_mix_with)}. They all should be filled!")

        if not exists(root):
            raise ValueError(f"Directory {repr(root)} doesn't exist")
        
        mixing_path = join(root, mixing) 
        to_mix_with_path = join(root, to_mix_with)

        if not exists(mixing_path):
            raise ValueError(f"Directory {repr(mixing_path)} doesn't exist")

        if not exists(to_mix_with_path):
            raise ValueError(f"Directory {repr(to_mix_with_path)} doesn't exist")

        self.__mixing : List[Image] = list()
        self.__to_mix_with : List[Image] = list()
        self.__logger : Logger = logger
        self.__mixing_mutations : List[MutationProcessor] = list()
        self.__to_mix_with_mutations : List[MutationProcessor] = list()

        self.__pasting_rule : PastingRule = DefaultPastingRule()
        
        for path, _, files in walk(root):
            if path == mixing_path:
                self.__mixing.extend([ImageFactory.open(join(mixing_path, f)).convert("RGBA") for f in files])
            elif path == to_mix_with_path:
                self.__to_mix_with.extend([ImageFactory.open(join(to_mix_with_path, f)).convert("RGBA") for f in files])
    
        if len(self.__mixing) == 0 or len(self.__to_mix_with) == 0:
            raise ValueError(f'Mixing or to mix with collections were empty. Both catalogs {mixing_path}, {to_mix_with_path} should be filled')

    def mix(self, mixing_samples: int, to_mix_with_samples: int) -> Iterable[MixedObject]:

        for _ in range(mixing_samples):
            mixing_idx = randint(0, len(self.__mixing)-1)

            for _ in range(to_mix_with_samples):

                to_mix_with_idx = randint(0, len(self.__to_mix_with)-1)
                
                to_mix_with_copied_image : Image = self.__to_mix_with[to_mix_with_idx].copy()
                mixing_copied_image : Image = self.__mixing[mixing_idx].copy()

                for mut in self.__to_mix_with_mutations:
                    to_mix_with_copied_image = mut.mutate(to_mix_with_copied_image)

                for mut in self.__mixing_mutations:
                    mixing_copied_image = mut.mutate(mixing_copied_image)

                rule = list(self.__pasting_rule.rule())

                if rule[0] + to_mix_with_copied_image.width > mixing_copied_image.width:
                    rule[0] = mixing_copied_image.width - to_mix_with_copied_image.width
                elif rule[0] + to_mix_with_copied_image.width < 0:
                    rule[0] = 0
                if rule[1] + to_mix_with_copied_image.height > mixing_copied_image.height:
                    rule[1] = mixing_copied_image.height - to_mix_with_copied_image.height
                elif rule[1] + to_mix_with_copied_image.height < 0:
                    rule[1] = 0

                box = Box(*rule, to_mix_with_copied_image.width, to_mix_with_copied_image.height)

                mixing_copied_image.paste(to_mix_with_copied_image, rule, mask=to_mix_with_copied_image)
                yield MixedObject(mixing_copied_image, box)

    def paste_as(self, pasting_rule : PastingRule) -> 'MixingDataset':
        self.__pasting_rule = pasting_rule
        return self

    def add_mutation_mixing(self, mutation_processor : MutationProcessor) -> 'MixInDataset':
        self.__mixing_mutations.append(mutation_processor)
        return self

    def add_mutation_to_mix_with(self, mutation_processor : MutationProcessor) -> 'MixInDataset':
        self.__to_mix_with_mutations.append(mutation_processor)
        return self