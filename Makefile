format:
	./format.sh

lint:
	./lint.sh

package:
	pyinstaller -i iMorphUpdater.ico --paths ./.venv/lib/python3.9/site-packages --onefile -y --console --name iMorphUpdater --noupx imorph_updater/__main__.py

run:
	python imorph_updater --noconfirm  