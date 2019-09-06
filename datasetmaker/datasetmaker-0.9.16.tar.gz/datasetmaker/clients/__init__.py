from .mynewsflash import MyNewsFlashClient
from .oecd import OECD
from .skolverket import SKVClient
from .wikipedia import Wikipedia
from .worldbank import WorldBank
from .unsc import UNSC
from .nobel import NobelClient
from .hdi import HDI
from .sipri import SIPRI
from .esv import ESVClient
from .socialstyrelsen import SocialstyrelsenClient
from .valforsk import ValforskClient


available = {
    'mynewsflash': MyNewsFlashClient,
    'oecd': OECD,
    'skolverket': SKVClient,
    'unsc': UNSC,
    'wikipedia': Wikipedia,
    'worldbank': WorldBank,
    'nobel': NobelClient,
    'hdi': HDI,
    'sipri': SIPRI,
    'esv': ESVClient,
    'socialstyrelsen': SocialstyrelsenClient,
    'valforsk': ValforskClient
}
