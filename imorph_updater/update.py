import asyncio
import glob
import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Tuple
from zipfile import ZipFile

from mega import Mega
from requests_html import HTMLSession

from .enums import WoWVersion
from .models import IMorphDTO

OWNED_CORE_LINK = "https://www.ownedcore.com/forums/wow-classic/wow-classic-bots-programs/935744-imorph-wow-classic.html"
DISCORD_LINK = "https://discord.gg/imorph-wow-morpher-459575858970230784"
DOWNLOAD_FOLDER = "iMorphs"


def imorph_update(noconfirm: bool, wow_versions: List[WoWVersion]) -> None:
    asyncio.run(_imorph_update(noconfirm, wow_versions))
    input("\nPress anything to close.")


def _download_imorph(imorph: IMorphDTO, user: Mega) -> None:
    print(f"Downloading `{imorph.full_name}` to `{DOWNLOAD_FOLDER}`")
    try:
        user.download_url(imorph.link, DOWNLOAD_FOLDER, dest_filename=imorph.zip_name)
    except PermissionError:
        return


def _cleanup(old_imorphs_paths: List[str]) -> None:
    def _clean_globs(globs: List[str], message_format: str = "Removing `%s`") -> None:
        for file in globs:
            print(message_format.format(file=file))
            if os.path.isdir(file):
                shutil.rmtree(file)
            if os.path.isfile(file):
                os.remove(file)

    _clean_globs(
        globs=glob.glob(f"{DOWNLOAD_FOLDER}/*.zip"),
        message_format="Removing downloaded iMorph archive `{file}`",
    )
    _clean_globs(
        globs=glob.glob(f"{tempfile.gettempdir()}/megapy*"),
        message_format="Removing temporary mega iMorph files `{file}`",
    )
    _clean_globs(
        globs=old_imorphs_paths,
        message_format="Removing old iMorph version `{file}`",
    )


def _extract_imorph(imorph: IMorphDTO) -> None:
    src = Path(f"{DOWNLOAD_FOLDER}/{imorph.zip_name}")
    dest = Path(f"{DOWNLOAD_FOLDER}/{imorph.full_name}")
    print(f"Extracting `{src}` to `{dest}`")
    with ZipFile(src, "r") as zip_file:
        zip_file.extractall(dest)


def _check_possible_imorphs_updates(
    wow_versions: List[WoWVersion],
) -> Tuple[List[IMorphDTO], List[str]]:
    imorphs = _get_imorphs(wow_versions)
    folders = glob.glob(f"{DOWNLOAD_FOLDER}/*iMorph*")
    old_imorphs: List[str] = []
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


def _get_imorphs(desired_versions: List[WoWVersion]) -> List[IMorphDTO]:
    imorph_type = "net"
    with HTMLSession() as session:
        response = session.get(OWNED_CORE_LINK)
        dtos = []
        first_post = response.html.find("blockquote", first=True)

        for version in desired_versions:
            """
            Match ownedforum post structure which is something among:
            <b>{version}</b>
            <br>
            <a href=SearchedLink>iMorph - x.xx.xx {imorph_type} [x.xx.x.xxxxxx]</a>
            """
            link = first_post.xpath(
                f"//b[text()[contains(., '{version}')]]"
                "/following-sibling::br"
                f"/following-sibling::a[.//b[text()='{imorph_type}']]",
                first=True,
            )
            if not link:
                continue

            dtos.append(
                IMorphDTO(
                    forum_name=link.text,
                    link=link.attrs["href"],
                    version=version,
                )
            )

        return dtos


async def _imorph_update(noconfirm: bool, wow_versions: List[WoWVersion]) -> None:
    print("Warning, before using new versions check on forum if it's safe!")
    print(f"iMorph Discord: {DISCORD_LINK}")
    print(f"iMorph forum thread: {OWNED_CORE_LINK}\n\n")
    print("Fetching download links from owned core..")
    mega_user = Mega().login()
    imorphs, old_imorphs_paths = _check_possible_imorphs_updates(wow_versions)

    if imorphs:
        for imorph in imorphs:
            print(f"Found new version: `{imorph.full_name}`")
        for old_imorph_path in old_imorphs_paths:
            print(f"Found existing old iMorph: `{old_imorph_path}`")
        if not noconfirm and input("Remove old and install new [Y/n]? ") not in [
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
