setup:
	mkdir ~/.virtualassistant
	cp -r ./src ~/.virtualassistant
	/usr/bin/env python3 -m venv ~/.virtualassistant/venv
	. ~/.virtualassistant/venv/bin/activate
	pip install -r ~/.virtualassistant/src/requirements.txt
	python -m spacy download en_core_web_sm

install:
	. ~/.virtualassistant/venv/bin/activate
	# install service
