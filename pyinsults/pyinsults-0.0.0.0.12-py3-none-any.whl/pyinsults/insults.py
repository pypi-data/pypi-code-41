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
  "maggot"


]

def random_insult():
    return random.choice(insults)

def long_insult():
    return ' '.join([random.choice(adjectives), random.choice(insults)])