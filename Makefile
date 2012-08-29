unit-test:
	PYTHONPATH=. nosetests tests/unit

requirements: requirements.pip
	pip install --requirement="requirements.pip"
