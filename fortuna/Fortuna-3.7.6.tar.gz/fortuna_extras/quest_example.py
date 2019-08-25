from Fortuna import TruffleShuffle


villager = TruffleShuffle({
    'armor smith', 'nerf herder', 'spice dealer', 'fool', 'dancer', 'sculptor', 'alchemist', 'goldsmith', 'miner',
    'bookbinder', 'stonemason', 'wet nurse', 'sailor', 'silversmith', 'leather worker', 'ship captain', 'falconer',
    'blacksmith', 'merchant', 'scribe', 'weaver', 'coin maker', 'tailor', 'poet', 'bartender', 'animal trainer',
    'fisherman', 'locksmith', 'brewer', 'weapon smith', 'wine vintner', 'quartermaster', 'herbalist', 'jeweler',
    'minstrel', 'chef', 'town crier', 'baker', 'butcher', 'juggler', 'shaman', 'fortuneteller', 'fire eater',
    'innkeeper', 'candlestick maker', 'teacher', 'potion salesman', 'pirate', 'artificer', 'farrier', 'playwright',
    'courtesan', 'glassblower', 'gypsy', 'midwife', 'messenger', 'barmaid', 'time keeper', 'musician', 'milkmaid',
    'astrologer'
})

item = TruffleShuffle({
    'bastard sword', 'battleaxe', 'bone splint tunic', 'breastplate', 'broom', 'buckler', 'chain mail tunic', 'cloak',
    'costume', 'crossbow', 'crude hide armor', 'dagger', 'field plate suit of armor', 'flail', 'formal robes', 'glaive',
    'greataxe', 'greatclub', 'greatsword', 'halberd', 'hand axe', 'heater shield', 'javelin', 'jousting shield', 'kilt',
    'kite shield', 'lance', 'leather jerkin', 'longbow', 'longsword', 'mace', 'maul', 'morningstar', 'noble garb',
    'padded gambeson', 'pair of gauntlets', 'pair of bracers', 'pike', 'quarterstaff', 'rapier', 'ring mail tunic',
    'round shield', 'scale mail suit of armor', 'scimitar', 'shortbow', 'shortsword', 'sickle', 'sling', 'spear',
    'studded leather doublet', 'tower shield', 'trident', 'villager garb', 'visor helm', 'war pick', 'warhammer', 'whip'
})


location = TruffleShuffle({
    "Spriteville", "Whiskey Straights", "Ashland Park", "Fishguard Village", "Winehill Valley", "Mead Garden"
})

wants_to = TruffleShuffle({
    "wants you to", "needs you to", "would like you to", "requests that you", "demands that you"
})

random_quest = TruffleShuffle({
    lambda: f"The {villager()} {wants_to()} steal the {item()} from the {villager()} in {location()}.",
    lambda: f"The {villager()} {wants_to()} give this {item()} to the {villager()} in {location()}.",
    lambda: f"The {villager()} {wants_to()} find the {item()} that the {villager()} lost in {location()}.",
    lambda: f"The {villager()} {wants_to()} rescue the {villager()}, last seen in {location()}.",
    lambda: f"The {villager()} {wants_to()} trade this {item()} to the {villager()} for their {item()}.",
})


if __name__ == "__main__":
    print()
    for _ in range(100):
        print(random_quest())
