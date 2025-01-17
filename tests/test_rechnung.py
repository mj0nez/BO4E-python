from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from bo4e.bo.geschaeftspartner import Geschaeftspartner
from bo4e.bo.rechnung import Rechnung
from bo4e.com.betrag import Betrag
from bo4e.com.rechnungsposition import Rechnungsposition
from bo4e.com.steuerbetrag import Steuerbetrag
from bo4e.com.zeitraum import Zeitraum
from bo4e.enum.geschaeftspartnerrolle import Geschaeftspartnerrolle
from bo4e.enum.rechnungsstatus import Rechnungsstatus
from bo4e.enum.rechnungstyp import Rechnungstyp
from bo4e.enum.steuerkennzeichen import Steuerkennzeichen
from bo4e.enum.waehrungscode import Waehrungscode
from bo4e.enum.zeiteinheit import Zeiteinheit
from tests.serialization_helper import assert_serialization_roundtrip
from tests.test_betrag import example_betrag
from tests.test_menge import example_menge
from tests.test_preis import example_preis
from tests.test_steuerbetrag import example_steuerbetrag

_rechnungsersteller = Geschaeftspartner(
    name1="Joachim",
    gewerbekennzeichnung=False,
    geschaeftspartnerrolle=[Geschaeftspartnerrolle.LIEFERANT],
)

_rechnungsempfaenger = Geschaeftspartner(
    name1="Helga",
    gewerbekennzeichnung=False,
    geschaeftspartnerrolle=[Geschaeftspartnerrolle.KUNDE],
)


class TestRechnung:
    @pytest.mark.parametrize(
        "rechnung",
        [
            pytest.param(
                Rechnung(
                    rechnungstitel="Hüpfburg",
                    rechnungsstatus=Rechnungsstatus.UNGEPRUEFT,
                    storno=True,
                    rechnungsnummer="202201211701",
                    rechnungsdatum=datetime.today(),
                    faelligkeitsdatum=datetime.today(),
                    rechnungstyp=Rechnungstyp.ENDKUNDENRECHNUNG,
                    original_rechnungsnummer="RE-2022-01-21_1701",
                    rechnungsperiode=Zeitraum(einheit=Zeiteinheit.TAG, dauer=Decimal(21)),
                    rechnungsersteller=_rechnungsersteller,
                    rechnungsempfaenger=_rechnungsempfaenger,
                    gesamtnetto=Betrag(wert=Decimal(12.5), waehrung=Waehrungscode.EUR),
                    gesamtsteuer=Betrag(wert=Decimal(12.5), waehrung=Waehrungscode.EUR),
                    gesamtbrutto=Betrag(wert=Decimal(12.5), waehrung=Waehrungscode.EUR),
                    vorausgezahlt=Betrag(wert=Decimal(12.5), waehrung=Waehrungscode.EUR),
                    rabatt_brutto=Betrag(wert=Decimal(12.5), waehrung=Waehrungscode.EUR),
                    zuzahlen=Betrag(wert=Decimal(12.5), waehrung=Waehrungscode.EUR),
                    steuerbetraege=[
                        Steuerbetrag(
                            steuerkennzeichen=Steuerkennzeichen.UST_19,
                            basiswert=Decimal(20.25),
                            waehrung=Waehrungscode.EUR,
                            steuerwert=Decimal(10.5),
                        )
                    ],
                    rechnungspositionen=[
                        Rechnungsposition(
                            positionsnummer=1,
                            lieferung_von=datetime(2021, 3, 15, tzinfo=timezone.utc),
                            lieferung_bis=datetime(2022, 3, 15, tzinfo=timezone.utc),
                            positionstext="Besonders wertvolle Rechnungsposition",
                            positions_menge=example_menge,
                            einzelpreis=example_preis,
                            teilsumme_netto=example_betrag,
                            teilsumme_steuer=example_steuerbetrag,
                        )
                    ],
                ),
                id="maximal attributes",
            ),
            pytest.param(
                Rechnung(
                    storno=True,
                    rechnungsnummer="202201211701",
                    rechnungsdatum=datetime.today(),
                    faelligkeitsdatum=datetime.today(),
                    rechnungstyp=Rechnungstyp.ENDKUNDENRECHNUNG,
                    original_rechnungsnummer="RE-2022-01-21_1701",
                    rechnungsperiode=Zeitraum(einheit=Zeiteinheit.TAG, dauer=Decimal(21)),
                    rechnungsersteller=_rechnungsersteller,
                    rechnungsempfaenger=_rechnungsempfaenger,
                    gesamtnetto=Betrag(wert=Decimal(12.5), waehrung=Waehrungscode.EUR),
                    gesamtsteuer=Betrag(wert=Decimal(12.5), waehrung=Waehrungscode.EUR),
                    gesamtbrutto=Betrag(wert=Decimal(12.5), waehrung=Waehrungscode.EUR),
                    zuzahlen=Betrag(wert=Decimal(12.5), waehrung=Waehrungscode.EUR),
                    rechnungspositionen=[
                        Rechnungsposition(
                            positionsnummer=1,
                            lieferung_von=datetime(2021, 3, 15, tzinfo=timezone.utc),
                            lieferung_bis=datetime(2022, 3, 15, tzinfo=timezone.utc),
                            positionstext="Besonders wertvolle Rechnungsposition",
                            positions_menge=example_menge,
                            einzelpreis=example_preis,
                            teilsumme_netto=example_betrag,
                            teilsumme_steuer=example_steuerbetrag,
                        )
                    ],
                ),
                id="minimal attributes",
            ),
        ],
    )
    def test_serialization_roundtrip(self, rechnung: Rechnung) -> None:
        """
        Test de-/serialisation
        """
        assert_serialization_roundtrip(rechnung)

    def test_missing_required_attribute(self) -> None:
        with pytest.raises(ValidationError) as excinfo:
            _ = Rechnung()  # type: ignore[call-arg]
        assert "13 validation errors" in str(excinfo.value)  # 13 from rechnung
