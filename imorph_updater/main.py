import asyncio
import glob
import os
import shutil
import tempfile
import typing as T
from pathlib import Path
from zipfile import ZipFile

from mega import Mega
from requests_html import HTMLSession

from .constants import DISCORD_LINK, DOWNLOAD_FOLDER, OWNED_CORE_LINK
from .models import IMorphDTO


async def _download_imorph(imorph: IMorphDTO, user: Mega) -> None:
    print(f"🔜 Downloading `{imorph.full_name}` to `{DOWNLOAD_FOLDER}`")
    try:
        user.download_url(imorph.link, DOWNLOAD_FOLDER, dest_filename=imorph.zip_name)
    except PermissionError:
        return


def _clean_temp_files() -> None:
    temp_dir = tempfile.gettempdir()
    for filename in glob.glob(f"{temp_dir}/megapy*"):
        print(f"🗑️  Removing temporary mega imorph files `{filename}`")
        os.remove(filename)


def _clean_archives() -> None:
    for filename in glob.glob(f"{DOWNLOAD_FOLDER}/*.zip"):
        print(f"🗑️  Removing downloaded archive `{filename}`")
        os.remove(filename)


def _cleanup_imorph() -> None:
    _clean_archives()
    _clean_temp_files()


def _extract_imorph(imorph: IMorphDTO) -> None:
    src = Path(f"{DOWNLOAD_FOLDER}/{imorph.zip_name}")
    dest = Path(f"{DOWNLOAD_FOLDER}/{imorph.full_name}")
    print(f"📁 Extracting `{src}` to `{dest}`")
    with ZipFile(src, "r") as zip_file:
        zip_file.extractall(dest)


def _check_imorphs() -> T.List[IMorphDTO]:
    imorphs = _get_imorph_dtos()
    folders = glob.glob(f"{DOWNLOAD_FOLDER}/*iMorph*")
    if not folders:
        return imorphs
    updatedable_imorphs = []
    for imorph in imorphs:
        if any(imorph.full_name in folder for folder in folders):
            continue
        updatedable_imorphs.append(imorph)
        old_imorphs = glob.glob(f"{DOWNLOAD_FOLDER}/*{imorph.version:s} - *")
        if old_imorphs:
            for old_imorph in old_imorphs:
                print(f"🗑️  Removing old iMorph version `{old_imorph}`")
                shutil.rmtree(old_imorph)
    return updatedable_imorphs


def _get_imorph_dtos() -> T.List[IMorphDTO]:
    with HTMLSession() as session:
        response = session.get(OWNED_CORE_LINK)
        return [
            IMorphDTO(forum_name=link.element.text, link=link.attrs["href"])
            for link in response.html.find("a[target='_blank'][href*='mega.nz']")
            if "(" not in link.element.text
        ]


async def _main() -> None:
    mega_user = Mega().login()
    Path("imorphs").mkdir(parents=True, exist_ok=True)
    imorphs = _check_imorphs()
    print("📋 Fetched download links from owned core.")
    if imorphs:
        for imorph in imorphs:
            print(f"✅ Found new version: {imorph.full_name}")
        print("❗ Warning, before using new versions check on forum if it's safe!")
        print(f"📺 iMorph Discord: {DISCORD_LINK}")
        print(f"📺 iMorph forum thread: {OWNED_CORE_LINK}\n\n")
        if input("❓ Proceed [Y/n]? ") not in ["y", "yes", "YES", "Y"]:
            return
    else:
        print("✅ No new versions found.")
        return
    for imorph in imorphs:
        await _download_imorph(imorph, mega_user)
        _extract_imorph(imorph)
    _cleanup_imorph()
    input("✨ All good! ✨")


def imorph_run() -> None:
    asyncio.run(_main())
