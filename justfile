set shell := ["powershell.exe", "-c"]
SOURCE := "imorph-updater"

lint:
	isort $(SOURCE) \
	&& black $(SOURCE) \
	&& mypy $(SOURCE) \
	&& pylint -j 4 $(SOURCE)



run:
	python {{SOURCE}}/main.py