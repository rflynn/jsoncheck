
analyze:
	flake8 --ignore E201,E202,E221,E226,E241,E261,E302,E321,E501,E701 src/__init__.py

test:
	nosetests src/__init__.py
