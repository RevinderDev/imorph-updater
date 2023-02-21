SOURCE="imorph_updater"

lint:
	isort $(SOURCE) \
	&& black $(SOURCE) \
	&& mypy $(SOURCE) \
	&& pylint -j 4 $(SOURCE)

package:
	pyinstaller --onefile -y --console --name IMorphUpdater --noupx runner.py

run:
	python runner.py