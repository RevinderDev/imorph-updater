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


def imorph_update(noconfirm: bool = False) -> None:
    asyncio.run(_imorph_update(noconfirm))
    input("\nPress anything to close.")


def _download_imorph(imorph: IMorphDTO, user: Mega) -> None:
    print(f"Downloading `{imorph.full_name}` to `{DOWNLOAD_FOLDER}`")
    try:
        user.download_url(imorph.link, DOWNLOAD_FOLDER, dest_filename=imorph.zip_name)
    except PermissionError:
        return


def _clean_globs(globs: T.List[str], message_format: str = "Removing `%s`") -> None:
    for glob in globs:
        print(message_format.format(glob=glob))
        if os.path.isdir(glob):
            shutil.rmtree(glob)
        if os.path.isfile(glob):
            os.remove(glob)


def _cleanup(old_imorphs_paths: T.List[str]) -> None:
    _clean_globs(
        globs=glob.glob(f"{DOWNLOAD_FOLDER}/*.zip"),
        message_format="Removing downloaded iMorph archive `{glob}`",
    )
    _clean_globs(
        globs=glob.glob(f"{tempfile.gettempdir()}/megapy*"),
        message_format="Removing temporary mega iMorph files `{glob}`",
    )
    _clean_globs(
        globs=old_imorphs_paths,
        message_format="Removing old iMorph version `{glob}`",
    )


def _extract_imorph(imorph: IMorphDTO) -> None:
    src = Path(f"{DOWNLOAD_FOLDER}/{imorph.zip_name}")
    dest = Path(f"{DOWNLOAD_FOLDER}/{imorph.full_name}")
    print(f"Extracting `{src}` to `{dest}`")
    with ZipFile(src, "r") as zip_file:
        zip_file.extractall(dest)


def _check_imorphs() -> T.Tuple[T.List[IMorphDTO], T.List[str]]:
    imorphs = _get_imorph_dtos()
    folders = glob.glob(f"{DOWNLOAD_FOLDER}/*iMorph*")
    old_imorphs: list = []
    if not folders:
        print("No old iMorph versions found.")
        return (imorphs, old_imorphs)
    updatedable_imorphs = []
    for imorph in imorphs:
        if any(imorph.full_name in folder for folder in folders):
            continue
        old_imorphs.extend(glob.glob(f"{DOWNLOAD_FOLDER}/*{imorph.version:s} - *"))
        updatedable_imorphs.append(imorph)
    return (updatedable_imorphs, old_imorphs)


def _get_imorph_dtos() -> T.List[IMorphDTO]:
    with HTMLSession() as session:
        response = session.get(OWNED_CORE_LINK)
        return [
            IMorphDTO(forum_name=link.element.text, link=link.attrs["href"])
            for link in response.html.find("a[target='_blank'][href*='mega.nz']")
            if "(" not in link.element.text
        ]


async def _imorph_update(noconfirm: bool) -> None:
    print("Warning, before using new versions check on forum if it's safe!")
    print(f"iMorph Discord: {DISCORD_LINK}")
    print(f"iMorph forum thread: {OWNED_CORE_LINK}\n\n")
    mega_user = Mega().login()
    print("Fetching download links from owned core..")
    imorphs, old_imorphs_paths = _check_imorphs()

    if imorphs:
        for imorph in imorphs:
            print(f"Found new version: `{imorph.full_name}`")
        for old_imorph_path in old_imorphs_paths:
            print(f"Found existing old iMorph: `{old_imorph_path}`")
        if not noconfirm:
            if input("Remove old and install new [Y/n]? ") not in [
                "y",
                "yes",
                "YES",
                "Y",
            ]:
                return
    else:
        print("No new versions found.")
        return
    Path(DOWNLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
    for imorph in imorphs:
        _download_imorph(imorph, mega_user)
        _extract_imorph(imorph)
    _cleanup(old_imorphs_paths)

    print("All good!")
