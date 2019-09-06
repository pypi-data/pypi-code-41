
import sys
from mtga.models.card import Card
from mtga.models.card_set import Set
import inspect


Plains = Card(name="plains", pretty_name="Plains", cost=[],
              color_identity=['W'], card_type="Land", sub_types="Plains",
              abilities=[], set_id="AKH", rarity="Basic", collectible=True, set_number=256,
              mtga_id=65363)
Island = Card(name="island", pretty_name="Island", cost=[],
              color_identity=['U'], card_type="Land", sub_types="Island",
              abilities=[], set_id="AKH", rarity="Basic", collectible=True, set_number=258,
              mtga_id=65369)
Swamp = Card(name="swamp", pretty_name="Swamp", cost=[],
             color_identity=['B'], card_type="Land", sub_types="Swamp",
             abilities=[], set_id="AKH", rarity="Basic", collectible=True, set_number=262,
             mtga_id=65379)
Mountain = Card(name="mountain", pretty_name="Mountain", cost=[],
                color_identity=['R'], card_type="Land", sub_types="Mountain",
                abilities=[], set_id="AKH", rarity="Basic", collectible=True, set_number=264,
                mtga_id=65385)
Forest = Card(name="forest", pretty_name="Forest", cost=[],
              color_identity=['G'], card_type="Land", sub_types="Forest",
              abilities=[], set_id="AKH", rarity="Basic", collectible=True, set_number=267,
              mtga_id=65393)


clsmembers = [card for name, card in inspect.getmembers(sys.modules[__name__]) if isinstance(card, Card)]
Amonkhet = Set("akh", cards=clsmembers)

set_ability_map = {}
