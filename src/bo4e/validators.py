"""
Contains validators for BO s and COM s classes.
"""
import re
from datetime import datetime
from typing import Any, Callable, Optional, Protocol, TypeVar

from pydantic import BaseModel, model_validator
from pydantic._internal import _decorators
from pydantic_core.core_schema import ValidationInfo

from bo4e.enum.aufabschlagstyp import AufAbschlagstyp
from bo4e.enum.waehrungseinheit import Waehrungseinheit

ModelT = TypeVar("ModelT", bound=BaseModel)


def combinations_of_fields(
    *fields: str,
    valid_combinations: set[tuple[int, ...]],
    custom_error_message: Optional[str] = None,
    custom_boolean_converter: Optional[Callable[[Any], bool]] = None,
) -> _decorators.PydanticDescriptorProxy[_decorators.ModelValidatorDecoratorInfo]:
    """
    A validator to check if a combination of fields is supplied with given allowed combinations.
    I.e. if you have a model with optional fields but only certain combinations of fields are allowed,
    you can use this validator to check if the supplied combination is valid.

    Note that the function returns a PydanticDescriptorProxy i.e. you only have to include something like
    `_my_validator = combinations_of_fields(...)` without using a call to e.g. `model_validator`.

    :param fields: the fields that should be checked
    :param valid_combinations: a set of tuples of 0 and 1 that indicate which fields are required. The length of the
        tuples should be equal to the number of fields. The order should be the same as the order of the fields.
        Otherwise, it could produce unexpected results.
    :param custom_error_message: a custom error message to be raised if the combination is invalid
    :param custom_boolean_converter: a custom function to convert the values of the fields to boolean values. The
        function should return True if the value is considered to be supplied and False otherwise. The default is to
        check if the value is not None and if the value is a string, if it is not empty.
    """
    if custom_boolean_converter is not None:
        supplied = custom_boolean_converter
    else:

        def supplied(value: Any) -> bool:
            return value is not None and (not isinstance(value, str) or value != "")

    def validator(cls: type[ModelT], data: dict[str, Any]) -> dict[str, Any]:
        bools = tuple(int(supplied(data.get(field, None))) for field in fields)
        if bools in valid_combinations:
            return data
        if custom_error_message:
            raise ValueError(custom_error_message)
        raise ValueError(f"Invalid combination of fields {fields} for {cls!r}: {bools}")

    return model_validator(mode="before")(validator)


# pylint:disable=unused-argument
def einheit_only_for_abschlagstyp_absolut(  # type: ignore[no-untyped-def]
    cls, value: Waehrungseinheit, validation_info: ValidationInfo
) -> Waehrungseinheit:
    """
    Check that einheit is only there if abschlagstyp is absolut.
    Currently, (2021-12-15) only used in COM AufAbschlag.
    """
    values = validation_info.data
    if value and (not values["auf_abschlagstyp"] or (values["auf_abschlagstyp"] != AufAbschlagstyp.ABSOLUT)):
        raise ValueError("Only state einheit if auf_abschlagstyp is absolute.")
    return value


# pylint:disable=too-few-public-methods
class _VonBisType(Protocol):
    """
    a protocol for all classes that have an inclusive start and exclusive end
    """

    @staticmethod
    def _get_inclusive_start(values: ValidationInfo) -> Optional[datetime]:
        """
        should return the inclusive start of the timeslice
        """

    # def _get_exclusive_end(self) -> Optional[datetime]:
    #     """
    #     should return the exclusive end of the timeslice
    #     """


def check_bis_is_later_than_von(cls, value: datetime, values: ValidationInfo):  # type: ignore[no-untyped-def]
    """
    assert that 'bis' is later than 'von'
    """
    # we want access to private methods here because these helper methods should be "hidden"
    start = cls._get_inclusive_start(values)  # pylint: disable=protected-access
    end = value
    if start and end and not end >= start:
        raise ValueError(f"The end '{end}' has to be later than the start '{start}'")
    return value


# pylint:disable=line-too-long
#: a regular expression that should match all OBIS Kennziffern
OBIS_PATTERN = r"((1)-((?:[0-5]?[0-9])|(?:6[0-5])):((?:[1-8]|99))\.((?:6|8|9|29))\.([0-9]{1,2})|(7)-((?:[0-5]?[0-9])|(?:6[0-5])):(.{1,2})\.(.{1,2})\.([0-9]{1,2}))"
# TODO: Maybe create custom data type for OBIS. See https://pydantic-docs.helpmanual.io/usage/types/#custom-data-types

_malo_id_pattern = re.compile(r"^[1-9]\d{10}$")


# pylint: disable=unused-argument
def validate_marktlokations_id(  # type: ignore[no-untyped-def]
    cls, marktlokations_id: str, values: ValidationInfo
) -> str:
    """
    A validator for marktlokations IDs
    """
    if not marktlokations_id:
        raise ValueError("The marktlokations_id must not be empty.")
    if not _malo_id_pattern.match(marktlokations_id):
        raise ValueError(f"The Marktlokations-ID '{marktlokations_id}' does not match {_malo_id_pattern.pattern}")
    expected_checksum = _get_malo_id_checksum(marktlokations_id)
    actual_checksum = marktlokations_id[10:11]
    if expected_checksum != actual_checksum:
        # pylint: disable=line-too-long
        raise ValueError(
            f"The Marktlokations-ID '{marktlokations_id}' has checksum '{actual_checksum}' but '{expected_checksum}' was expected."
        )
    return marktlokations_id


def _get_malo_id_checksum(malo_id: str) -> str:
    """
    Get the checksum of a marktlokations id.
    a) Quersumme aller Ziffern in ungerader Position
    b) Quersumme aller Ziffern auf gerader Position multipliziert mit 2
    c) Summe von a) und b) d) Differenz von c) zum nächsten Vielfachen von 10 (ergibt sich hier 10, wird die
       Prüfziffer 0 genommen
    https://bdew-codes.de/Content/Files/MaLo/2017-04-28-BDEW-Anwendungshilfe-MaLo-ID_Version1.0_FINAL.PDF
    :return: the checksum as string
    """
    odd_checksum: int = 0
    even_checksum: int = 0
    # start counting at 1 to be consistent with the above description
    # of "even" and "odd" but stop at tenth digit.
    for i in range(1, 11):
        digit = malo_id[i - 1 : i]
        if i % 2 - 1 == 0:
            odd_checksum += int(digit)
        else:
            even_checksum += 2 * int(digit)
    result: int = (10 - ((even_checksum + odd_checksum) % 10)) % 10
    return str(result)
