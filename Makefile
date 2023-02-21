SOURCE="imorph_updater"

lint:
	isort $(SOURCE) \
	&& black $(SOURCE) \
	&& mypy $(SOURCE) \
	&& pylint -j 4 $(SOURCE)

package:
	pyinstaller -i iMorphUpdater.ico --onefile -y --console --name iMorphUpdater --noupx runner.py

run:
	python runner.py --noconfirm  