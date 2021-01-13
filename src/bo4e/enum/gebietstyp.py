"""
Auflistung der möglichen Gebietstypen. (no shit, sherlock)
"""
from enum import Enum

_gebietstyp = {
    "REGELZONE": "REGELZONE",
    "MARKTGEBIET": "MARKTGEBIET",
    "BILANZIERUNGSGEBIET": "BILANZIERUNGSGEBIET",
    "VERTEILNETZ": "VERTEILNETZ",
    "TRANSPORTNETZ": "TRANSPORTNETZ",
    "REGIONALNETZ": "REGIONALNETZ",
    "AREALNETZ": "AREALNETZ",
    "GRUNDVERSORGUNGSGEBIET": "GRUNDVERSORGUNGSGEBIET",
    "VERSORGUNGSGEBIET": "VERSORGUNGSGEBIET",
}
Gebietstyp = Enum("Gebietstyp", _gebietstyp)
