import re
from dataclasses import dataclass, field

from .enums import WoWVersion


@dataclass
class IMorphDTO:
    forum_name: str
    link: str
    version: WoWVersion = field(init=False)

    def __post_init__(self) -> None:
        version_match = re.search(r"\[\d+.", self.forum_name)
        if version_match:
            self.version = WoWVersion.from_text(version_match.group())

    @property
    def full_name(self) -> str:
        return f"{self.version:s} - {self.forum_name}"

    @property
    def zip_name(self) -> str:
        return self.full_name + ".zip"
