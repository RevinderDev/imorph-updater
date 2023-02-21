import argparse

from imorph_updater import imorph_update

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-y",
        "--noconfirm",
        help="Auto confirm iMorph replacing/downloading.",
        action="store_true",
    )
    imorph_update(parser.parse_args().noconfirm)
