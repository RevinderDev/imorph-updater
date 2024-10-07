import re
import typing
from enum import Enum


class WoWVersion(str, Enum):
    """
    Regex examples:
        Classic     - iMorph - 1.3.29 (net) [1.14.3.49821]
        Classic SOM - iMorph - 1.4.30 (net) (menu) [3.4.1.49936]
        Retail      - iMorph - 1.4.27 (net) (menu) [10.1.0.50000]
    """

    CLASSIC_ERA = "Classic Era", re.compile(r"(\(net\)) \[(1.\d\d.\d.\d{5})\]")
    CLASSIC_CATACLYSM = (
        "Classic Cataclysm",
        re.compile(r"(\(net\)) \[(4.4.\d.\d{5})\]"),
    )
    RETAIL = "Retail The War Within", re.compile(r"(\(net\)) \[(1\d.\d.\d.\d{5})\]")

    @typing.no_type_check
    def __new__(cls, value: str, pattern: re.Pattern) -> "WoWVersion":
        entry = str.__new__(cls)
        entry._value_ = value
        entry._pattern = pattern
        return entry

    @property
    @typing.no_type_check
    def pattern(self) -> re.Pattern:
        return self._pattern
