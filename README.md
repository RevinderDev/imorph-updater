# CLI iMorph Updater
[<img src="https://img.shields.io/github/release/RevinderDev/imorph-updater">](https://github.com/RevinderDev/imorph-updater) [<img src="https://img.shields.io/github/downloads/RevinderDev/imorph-updater/latest/total">](https://github.com/RevinderDev/imorph-updater/releases/latest) [<img src="https://img.shields.io/github/downloads/RevinderDev/imorph-updater/total">](https://github.com/RevinderDev/imorph-updater/releases/latest) [<img src="https://img.shields.io/github/actions/workflow/status/RevinderDev/imorph-updater/build.yml">](https://github.com/RevinderDev/imorph-updater/actions)

CLI iMorph updater.
Features:  
* **Automatically** fetches new versions of iMorph from [OwnedCore](https://www.ownedcore.com/forums/wow-classic/wow-classic-bots-programs/935744-imorph-wow-classic.html)
* **Extracts** everything to predefined folder.
* **Cleans up** all temporary and unnecessary files.
* **Minimal** interaction required for total laziness.
* **Update** old version (when there is different version on forum, than the one locally - update it with new forum one and delete old one).
* **Windows** and **Linux** support.


<p align="center">
  <img src="https://i.imgur.com/jHJuI9e.png">
</p>

## Download

The latest release can be found [here](https://github.com/RevinderDev/imorph-updater/releases/latest).

## Running

By default it will download `Retail` imorph with `(net)` version as this is what I am using. See Windows and Cmdline sections for details. 


### For Windows

Double click `.exe` file and console window will pop up. 

**TIP**: If you wish to never have to confirm `Remove old and install new [Y/n]? ` prompt then do the following:
* Right click -> Create shortcut on `iMorphUpdater.exe`
* On shortcut: Right click -> Properties 
* add `-y` or `--noconfirm` to `Target` like so:
* add `-w` and list of expansions you want iMorph for e.g. `-w RETAIL CLASSIC_CATACLYSM`.

<p align="center">
  <img src="https://i.imgur.com/y02ds4Z.png">
</p>

### From command line
```
usage: imorph_updater [-h] [-y]
                      [-w CLASSIC_ERA,CLASSIC_CATACLYSM,RETAIL,CLASSIC_CHINA,RETAIL_CHINA]

optional arguments:
  -h, --help            show this help message and exit
  -y, --noconfirm       Auto confirm iMorph
                        replacing/downloading.
  -w CLASSIC_ERA,CLASSIC_CATACLYSM,RETAIL,CLASSIC_CHINA,RETAIL_CHINA 
                        Choose which WoWVersions iMorphs you
                        want to download
```

```
$ ./iMorphUpdater -y
$ ./iMorphUpdater
```
On linux make sure it has correct modes:
```
$ chmod +x iMorphUpdater
```


## Development & Contributing

Requirements:
- Poetry
- Python 3.9
- Linux recommended for easy `Makefile` access.

Installing dependencies:
```
$ poetry install
```

For linting:
```
$ make lint
```

For formatting:
```
$ make format
```


Building binary:

```
$ make package
```

Running on local `venv`:

```
$ make run
```
