clean:
	@rm -f dist/*
	@rm -rf build
	@find . -name '*.pyc' -or -name '*.pyo' -or -name '__pycache__' -type f -delete
	@find . -type d -empty -delete

dist: clean
	@python ./setup.py sdist bdist_wheel
