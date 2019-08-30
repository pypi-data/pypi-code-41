import random

adjectives = [

    "stinking",
    "whining",
    "pathetic",
    "ugly",
    "obnoxious",
    "low-life",
    "nasty-ass",
    "utter",
    "clueless",
    "weapons-grade",
    "weaselheaded",
    "toupéd",
    "witless",
    "backwards",
    "undercooked",
    "absolute",
    "monumental",
    "foolish",
    "ignorannt",
    "inbred",
    "half-assed",
    "Trump voting",
    "Boris Johnson",
    "ass leaking",
    "unwanted"
    "pointless",


]

insults = [
    "asshole",
    "moron",
    "cumstain",
    "foolio",
    "dickwad",
    "Trump voter",
    "Justin Bieber fan",
    "retard",
    "fuckface",
    "cocksmoker",
    "shitgoblin",
    "jizztrumpet",
    "goatfucker",
    "motherfucker",
    "faglord",
    "shitbag",
    "dickbag",
    "cockwomble",
    "fucknugget",
    "thundercunt",
    "numpty",
    "fleshbag",
    "cocksplat",
    "cabbage",
    "peasant",
    "farmer",
    "crayon chewer",
    "tosser",
    "git",
    "muppet",
    "plonker",
    "knob head",
    "bell end",
    "arsemonger",
    "maggot",
    "butthole",
    "blobfish",
    "pug",
    "soap eater",
    "windowlicker",
    "fart",
    "monkey",
    "fuckface",
    "mongoose",
    "twat",
    "cunt",
    "inbred",
    "worm",
    "square",
    "shitface",
    "skank",
    "dickhead",
    "piece of fuck",
    "dumbass",




]


def random_insult():
    return random.choice(insults)


def long_insult():
    return ' '.join([random.choice(adjectives), random.choice(insults)])
