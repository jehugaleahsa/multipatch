unit-test: virtualenv
	nosetests tests/unit

virtualenv:
	. env/bin/activate
