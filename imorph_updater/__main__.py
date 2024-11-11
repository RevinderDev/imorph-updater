import argparse

from imorph_updater import WoWVersion, imorph_update

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-y",
        "--noconfirm",
        help="Auto confirm iMorph replacing/downloading.",
        action="store_true",
    )
    choices = [version.name for version in WoWVersion]
    parser.add_argument(
        "-w",
        default=[],
        help="Choose which WoWVersions iMorphs you want to download",
        nargs="+",
        metavar=",".join(choices),
    )
    parsed_args = parser.parse_args()
    if not (wow_versions := parsed_args.w):
        wow_versions.append(WoWVersion.RETAIL.name)

    imorph_update(parsed_args.noconfirm, [WoWVersion[arg] for arg in wow_versions])
