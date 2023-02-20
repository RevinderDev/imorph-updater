from enum import Enum


class WoWVersion(str, Enum):
    CLASSIC = "Classic"
    CLASSIC_SOM = "Classic SOM"
    RETAIL = "Retail"

    @staticmethod
    def from_text(text: str) -> "WoWVersion":
        if text == "[1.":
            return WoWVersion.CLASSIC_SOM
        if text == "[3.":
            return WoWVersion.CLASSIC
        if text == "[10.":
            return WoWVersion.RETAIL
        assert False
