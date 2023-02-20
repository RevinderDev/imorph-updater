from requests_html import HTMLSession
import asyncio
from mega import Mega
import re
from dataclasses import dataclass
from enum import Enum
import typing as T
import tempfile
import glob
import os
from zipfile import ZipFile
from pathlib import Path
import shutil


OWNED_CORE_LINK = "https://www.ownedcore.com/forums/wow-classic/wow-classic-bots-programs/935744-imorph-wow-classic.html"



class WoWVersion(str, Enum):
    CLASSIC = "Classic"
    CLASSIC_SOM = "Classic SOM"
    RETAIL = "Retail"
    
    # TODO: Add from text

TEXT_TO_WOW_VERSION = {
    "[1.": WoWVersion.CLASSIC_SOM,
    "[3.": WoWVersion.CLASSIC,
    "[10.": WoWVersion.RETAIL
}

DOWNLOAD_FOLDER = "imorphs"


@dataclass
class IMorphDTO:
    forum_name: str
    link: str
    _wow_version: WoWVersion = ""
    
    @property
    def version(self) -> T.Optional[WoWVersion]:
        if not self._wow_version:
            version_match = re.search("\[\d+.", self.forum_name)
            if version_match:
                self._wow_version = TEXT_TO_WOW_VERSION.get(version_match.group())
        return self._wow_version
    
    @property
    def full_name(self) -> str:
        return f"{self.version:s} - {self.forum_name}"
        
    @property
    def zip_name(self) -> str:
        return self.full_name + ".zip"

async def download_imorph(imorph: IMorphDTO, user: Mega) -> None:
    print(f"🔜 Downloading `{imorph.full_name}` to `{DOWNLOAD_FOLDER}`")
    try:
        user.download_url(imorph.link, DOWNLOAD_FOLDER, dest_filename=imorph.zip_name)
    except PermissionError:
        pass

def cleaunp() -> None:
    temp_dir = tempfile.gettempdir()
    for filename in glob.glob(f"{temp_dir}/megapy*"):
        print(f'🗑️ Removing temporary mega imorph files `{filename}`')
        os.remove(filename) 
        
    for filename in glob.glob(f"{DOWNLOAD_FOLDER}/*.zip"):
        print(f"🗑️ Removing downloaded archive `{filename}`")
        os.remove(filename)
        
        
def extract_imorph(src: Path, dest: Path) -> None:
    print(f"📁 Extracting `{src}` to `{dest}`")
    with ZipFile(src, 'r') as zip_file:
        zip_file.extractall(dest)
        
        
def check_for_updates(imorphs: T.List[IMorphDTO]) -> T.List[IMorphDTO]:
    folders = glob.glob(f"{DOWNLOAD_FOLDER}/*iMorph*")
    if not folders:
        return imorphs
    updatedable_imorphs = []
    for imorph in imorphs:
        if any(imorph.full_name in folder for folder in folders):
            continue
        updatedable_imorphs.append(imorph)
        old_imorphs = glob.glob(f"{DOWNLOAD_FOLDER}/*{imorph.version:s}*")
        if old_imorphs:
            for old_imorph in old_imorphs:
                print(f"🗑️ Removing old iMorph version `{old_imorph}`") 
                shutil.rmtree(old_imorph)
    return updatedable_imorphs
    

async def main() -> None:
    mega_user = Mega().login()
    with HTMLSession() as session:
        response  = session.get(OWNED_CORE_LINK)
        imorphs = [IMorphDTO(forum_name=link.element.text, link=link.attrs['href']) 
                        for link in response.html.find("a[target='_blank'][href*='mega.nz']") 
                        if "(" not in link.element.text]
        download_folder = Path("imorphs")
        if os.path.exists(download_folder):
            imorphs = check_for_updates(imorphs)
        else:
            os.mkdir(download_folder)
        print(f"📋 Fetched download links from owned core.")
        for imorph in imorphs:
            await download_imorph(imorph, mega_user)
            extract_imorph(f"{DOWNLOAD_FOLDER}/{imorph.zip_name}", f"{DOWNLOAD_FOLDER}/{imorph.full_name}")
        cleaunp()
        print(f"✨ All good! ✨")


if __name__ == "__main__":
    asyncio.run(main())
