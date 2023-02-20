SOURCE="imorph_updater"

lint:
	isort $(SOURCE) \
	&& black $(SOURCE) \
	&& mypy $(SOURCE) \
	&& pylint -j 4 $(SOURCE)

package:
	pyinstaller --onefile -y --console --name IMorphUpdater --strip --noupx imorph_updater.py

run:
	python imorph_updater.py