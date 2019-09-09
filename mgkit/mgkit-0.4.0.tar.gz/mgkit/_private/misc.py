import itertools
from xml.etree import ElementTree

def find_reactions(reactions, orthologs):
    if isinstance(orthologs, str):
        orthologs = [orthologs]
    orthologs = set(orthologs)
    for reaction in reactions:
        if reaction.orthologs & orthologs:
            yield reaction, reaction.orthologs & orthologs
