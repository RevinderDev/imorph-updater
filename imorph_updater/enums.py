from enum import StrEnum


class WoWVersion(StrEnum):
    CLASSIC = "Classic"
    CLASSIC_SOM = "Classic SOM"
    RETAIL = "Retail"

    @staticmethod
    def from_text(text: str) -> "WoWVersion":
        match text:
            case "[1.":
                return WoWVersion.CLASSIC_SOM
            case "[3.":
                return WoWVersion.CLASSIC
            case "[10.":
                return WoWVersion.RETAIL
            case _:
                assert False
