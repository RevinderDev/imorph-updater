# TUI iMorph Updater

CLI iMorph updater.
Features:  
* Automatically fetches new versions of iMorph from [OwnedCore](https://www.ownedcore.com/forums/wow-classic/wow-classic-bots-programs/935744-imorph-wow-classic.html)
* Extracts everything to predefined folder.
* Cleans up all temporary and unnecessary files.
* Minimal interaction required for total laziness.
* Windows and Linux support.

![SS](https://i.imgur.com/jHJuI9e.png)


## Download

TODO:

## Running from CL

```
usage: iMorphUpdater [-h] [-y]

optional arguments:
  -h, --help       show this help message and exit
  -y, --noconfirm  Auto confirm iMorph replacing/downloading.
```

```
$ ./iMorphUpdater -y
$ ./iMorphUpdater
```


## Development & Contributing

Requirements:
- poetry
- python 3.9
- Linux recommended for easy `Makefile` access.

For linting use:
```
$ make lint
```

Building binary:

```
$ make package
```

Running on local `venv`:

```
$ make run
```