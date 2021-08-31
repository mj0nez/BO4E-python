"""
Einheit: Messgrößen, die per Messung oder Vorgabe ermittelt werden können.
"""
from enum import Enum

_mengeneinheit = {
    "W": "W",  # Watt
    "WH": "WH",  # Wattstunde
    "KW": "KW",  # Kilowatt
    "KWH": "KWH",  # Kilowattstunde
    "KVARH": "KVARH",  # Kilovarstunde
    "MW": "MW",  # Megawatt
    "MWH": "MWH",  # Megawattstunde
    "STUECK": "STUECK",  # Stückzahl
    "KUBIKMETER": "KUBIKMETER",  # Kubikmeter (Gas)
    "STUNDE": "STUNDE",  # Stunde
    "TAG": "TAG",  # Tage
    "MONAT": "MONAT",  # Monat
    "JAHR": "JAHR",  # Jahr
    "PROZENT": "PROZENT",  # Prozent
}
Mengeneinheit = Enum("Mengeneinheit", _mengeneinheit)
