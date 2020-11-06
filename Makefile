VENV_NAME?=venv
PYTHON=$(PWD)/$(VENV_NAME)/bin/python
PIP=$(PWD)/$(VENV_NAME)/bin/pip
export DATA_DIR = $(PWD)server/datasets


venv: FORCE
	test -d $(VENV_NAME) || python3 -m venv $(VENV_NAME)
	. $(VENV_NAME)/bin/activate

install: venv
	$(PIP) install -r server/requirements.txt
	@cd ui; npm install
	@$(PYTHON) -m spacy download en_core_web_sm

build: venv
	npm build app/react-app

test: venv
	cd server; $(PYTHON) -m unittest discover

server: venv
	cd server; $(PYTHON) api/server.py

ui: venv
	cd ui; npm start

gitclean:
	#TODO

uninstall:
	#TODO

FORCE: