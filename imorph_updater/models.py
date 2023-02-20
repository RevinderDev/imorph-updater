import re
import typing as T
from dataclasses import dataclass

from .enums import WoWVersion


@dataclass
class IMorphDTO:
    forum_name: str
    link: str
    _wow_version: T.Optional[WoWVersion] = None

    @property
    def version(self) -> T.Optional[WoWVersion]:
        if not self._wow_version:
            version_match = re.search(r"\[\d+.", self.forum_name)
            if version_match:
                self._wow_version = WoWVersion.from_text(version_match.group())
        return self._wow_version

    @property
    def full_name(self) -> str:
        return f"{self.version:s} - {self.forum_name}"

    @property
    def zip_name(self) -> str:
        return self.full_name + ".zip"
