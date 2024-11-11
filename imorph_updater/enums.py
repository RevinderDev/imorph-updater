from enum import Enum


class WoWVersion(str, Enum):
    CLASSIC_ERA = "Classic Era"
    CLASSIC_CATACLYSM = "Classic Cataclysm"
    RETAIL = "Retail The War Within"
    CLASSIC_CHINA = "Classic WotLK China"
    RETAIL_CHINA = "Retail The War Within China"
