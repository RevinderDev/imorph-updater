from dataclasses import dataclass

from .enums import WoWVersion


@dataclass
class IMorphDTO:
    forum_name: str
    link: str
    version: WoWVersion

    @property
    def full_name(self) -> str:
        return f"{self.version:s} - {self.forum_name}"

    @property
    def zip_name(self) -> str:
        return self.full_name + ".zip"
